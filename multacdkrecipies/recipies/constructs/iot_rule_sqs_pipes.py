from copy import deepcopy

from aws_cdk import (
    core,
    aws_iot as iot,
    aws_lambda_event_sources as lambda_sources,
)
from multacdkrecipies.common import base_alarm, base_iot_rule, base_lambda_function, base_queue, base_sqs_role
from multacdkrecipies.recipies.utils import IOT_SQS_CONFIG_SCHEMA, validate_configuration


class AwsIotRulesSqsPipes(core.Construct):
    """
    AWS CDK Construct that defines a pipe where a Rules captures an MQTT Message sent to or from AWS IoT MQTT Broker,
    then the message is sent to an SQS Queue and a Lambda function or functions subscribed to the topic can process it
    and take proper actions. The construct allows to set alerts on both resources the SQS Queue and the
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
        validate_configuration(configuration_schema=IOT_SQS_CONFIG_SCHEMA, configuration_received=self._configuration)

        # Defining SQS Queue
        queue_data = deepcopy(self._configuration["queue"])
        self._sqs_queue = base_queue(construct=self, **queue_data)

        # Defining IAM Role
        role = base_sqs_role(self, resource_name=queue_data["queue_name"], principal_resource="iot")

        # Validating Lambda Function Runtime
        functions_data = self._configuration["lambda_handlers"]
        self._lambda_functions = list()
        for lambda_function in functions_data:
            _lambda_function = base_lambda_function(self, **lambda_function)
            self._lambda_functions.append(_lambda_function)

            _lambda_function.add_event_source(lambda_sources.SqsEventSource(queue=self._sqs_queue, batch_size=10))

        # Defining Topic Rule properties
        action = iot.CfnTopicRule.SqsActionProperty(queue_url=self._sqs_queue.queue_url, role_arn=role.role_arn)
        action_property = iot.CfnTopicRule.ActionProperty(sqs=action)

        rule_data = self._configuration["iot_rule"]
        self._iot_rule = base_iot_rule(self, action_property=action_property, **rule_data)

    def set_alarms(self):
        """
        Function that set alarms for the resources involved in the construct. Except the IoT Rule.
        :return: None
        """
        if isinstance(self._configuration["queue"].get("alarms"), list) is True:
            sqs_alarms = list()
            for alarm_definition in self._configuration["queue"].get("alarms"):
                sqs_alarms.append(
                    base_alarm(
                        self,
                        resource_name=self._configuration["queue"]["queue_name"],
                        base_resource=self._sqs_queue,
                        **alarm_definition,
                    )
                )

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
    def sqs_queue(self):
        """
        :return: Construct SQS Queue.
        """
        return self._sqs_queue

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
