from copy import deepcopy

from aws_cdk import (
    core,
    aws_iot as iot,
    aws_lambda_event_sources as event_src,
)
from multacdkrecipies.common import (
    base_alarm,
    base_iot_rule,
    base_lambda_function,
    base_kinesis_role,
    base_kinesis_stream,
)
from multacdkrecipies.recipies.utils import IOT_KINESIS_CONFIG_SCHEMA, validate_configuration


class AwsIotRulesKinesisPipes(core.Construct):
    """
    AWS CDK Construct that defines a pipe where a Rules captures an MQTT Message sent to or from AWS IoT MQTT Broker,
    then the message is sent to an SNS Topic and a Lambda function or functions subscribed to the topic can process it
    and take proper actions. The construct allows to set alerts on both resources the SNS Topic and the
    Lambda Functions.
    """

    def __init__(self, scope: core.Construct, id: str, *, prefix: str, environment: str, configuration, **kwargs):
        """
        :param scope: Stack class, used by CDK.
        :param id: ID of the construct, used by CDK.
        :param prefix: Prefix of the construct, used for naming purposes.
        :param environment: Environment of the construct, used for naming purposes.
        :param configuration: Configuration of the construct. In this case IOT_SNS_CONFIG_SCHEMA.
        :param kwargs: Other parameters that could be used by the construct.
        """
        super().__init__(scope, id, **kwargs)
        self.prefix = prefix
        self.environment_ = environment
        self._configuration = configuration

        # Validating that the payload passed is correct
        validate_configuration(configuration_schema=IOT_KINESIS_CONFIG_SCHEMA, configuration_received=self._configuration)

        # Defining Kinesis Stream
        stream_data = deepcopy(self._configuration["stream"])
        self._kinesis_stream = base_kinesis_stream(self, **stream_data)

        # Defining IAM Role
        role = base_kinesis_role(self, resource_name=stream_data["stream_name"], principal_resource="iot")

        # Validating Lambda Function Runtime
        functions_data = self._configuration["lambda_handlers"]
        self._lambda_functions = list()
        for setting in functions_data:
            _lambda_function = base_lambda_function(self, **setting["lambda_handler"])
            self._lambda_functions.append(_lambda_function)

            # Defining Function Subscription
            event_source = event_src.KinesisEventSource(stream=self._kinesis_stream, **setting["event_settings"])
            _lambda_function.add_event_source(event_source)

        # Defining Topic Rule properties
        action = iot.CfnTopicRule.KinesisActionProperty(stream_name=self._kinesis_stream.stream_name, role_arn=role.role_arn)
        action_property = iot.CfnTopicRule.ActionProperty(kinesis=action)

        rule_data = self._configuration["iot_rule"]
        self._iot_rule = base_iot_rule(self, action_property=action_property, **rule_data)

    def set_alarms(self):
        """
        Function that set alarms for the resources involved in the construct. Except the IoT Rule.
        :return: None
        """
        for lambda_function_data, lambda_function_definition in zip(
            self._configuration["lambda_handlers"], self._lambda_functions
        ):
            if isinstance(lambda_function_data.get("alarms"), list) is True:
                lambda_alarms = list()
                for alarm_definition in lambda_function_data.get("alarms"):
                    lambda_alarms.append(
                        base_alarm(
                            self,
                            resource_name=lambda_function_data.get("lambda_name"),
                            base_resource=lambda_function_definition,
                            **alarm_definition,
                        )
                    )

    @property
    def configuration(self):
        """
        :return: Construct configuration.
        """
        return self._configuration

    @property
    def kinesis_stream(self):
        """
        :return: Construct Kinesis Stream.
        """
        return self._kinesis_stream

    @property
    def lambda_functions(self):
        """
        :return: List of Constructs Lambda Functions.
        """
        return self._lambda_functions

    @property
    def iot_rule(self):
        """
        :return: Construct IoT Rule.
        """
        return self._iot_rule
