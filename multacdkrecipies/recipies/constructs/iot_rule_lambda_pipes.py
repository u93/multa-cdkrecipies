from aws_cdk import (
    core,
    aws_iot as iot,
)
from multacdkrecipies.common import base_alarm, base_iot_rule, base_lambda_function
from multacdkrecipies.recipies.utils import IOT_LAMBDA_CONFIG_SCHEMA, validate_configuration


class AwsIotRulesLambdaPipes(core.Construct):
    """
    AWS CDK Construct that defines a pipe where a Rules captures an MQTT Message sent to or from AWS IoT MQTT Broker,
    then the message is sent to a Lambda function for  processing and take proper actions.
    The construct allows to set alerts on the Lambda Functions.
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
        validate_configuration(configuration_schema=IOT_LAMBDA_CONFIG_SCHEMA, configuration_received=self._configuration)

        # Validating Lambda Function Runtime
        functions_data = self._configuration["lambda_handler"]
        self._lambda_function = base_lambda_function(self, **functions_data)

        # Defining Topic Rule properties
        action = iot.CfnTopicRule.LambdaActionProperty(function_arn=self._lambda_function.function_arn)
        action_property = iot.CfnTopicRule.ActionProperty(lambda_=action)

        rule_data = self._configuration["iot_rule"]
        self._iot_rule = base_iot_rule(self, action_property=action_property, **rule_data)

    def set_alarms(self):
        """
        Function that set alarms for the resources involved in the construct. Except the IoT Rule.
        :return: None
        """

        lambda_function_data = self._configuration["lambda_handler"]
        if isinstance(lambda_function_data.get("alarms"), list) is True:
            lambda_alarms = list()
            for alarm_definition in lambda_function_data.get("alarms"):
                lambda_alarms.append(
                    base_alarm(
                        self,
                        resource_name=lambda_function_data.get("lambda_name"),
                        base_resource=self._lambda_function,
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
    def lambda_functions(self):
        """
        :return: Construct Lambda Function.
        """
        return self._lambda_function

    @property
    def iot_rule(self):
        """
        :return: Construct IoT Rule.
        """
        return self._iot_rule
