from copy import deepcopy

from aws_cdk import (
    core,
    aws_iot as iot,
    aws_sns_subscriptions as sns_subs,
)
from .common import base_alarm, base_iot_rule, base_lambda_function, base_sns_role, base_topic
from .utils import IOT_SNS_CONFIG_SCHEMA, validate_configuration


class AwsIotRulesSnsPipes(core.Construct):
    """
    AWS CDK Construct that defines a pipe where a Rules captures an MQTT Message sent to or from AWS IoT MQTT Broker,
    then the message is sent to an SNS Topic and a Lambda function subscribed to the topic can process it and take
    proper actions. The construct takes a few inputs.

    Attributes:
        prefix (str): The prefix set on the name of each resource created in the stack. Just for organization purposes.
        environment_ (str): The environment that all resources will use. Also for organizational and testing purposes.
        _sns_topic (object): SNS Topic representation in CDK.
        _lambda_function (object): Lambda Function representation in CDK.
        _iot_rule (object): IoT Topic Rule representation in CDK.

    """

    def __init__(self, scope: core.Construct, id: str, *, prefix: str, environment: str, configuration, **kwargs):
        """

        :param scope:
        :param id:
        :param prefix:
        :param environment:
        :param configuration:
        :param kwargs:
        """
        super().__init__(scope, id, **kwargs)
        self.prefix = prefix
        self.environment_ = environment
        self._configuration = configuration

        # Validating that the payload passed is correct
        validate_configuration(configuration_schema=IOT_SNS_CONFIG_SCHEMA, configuration_received=self._configuration)

        # Defining SNS Topic
        topic_data = deepcopy(self._configuration["topic"])
        self._sns_topic = base_topic(self, **topic_data)

        # Defining IAM Role
        role = base_sns_role(self, resource_name=topic_data["topic_name"], principal_resource="iot")

        # Validating Lambda Function Runtime
        functions_data = self._configuration["lambda_handlers"]
        self._lambda_functions = list()
        for lambda_function in functions_data:
            _lambda_function = base_lambda_function(self, **lambda_function)
            self._lambda_functions.append(_lambda_function)

            # Defining the Lambda subscription to the specified SNS Topic in cdk.json file.
            sns_subscription = sns_subs.LambdaSubscription(fn=_lambda_function)
            self._sns_topic.add_subscription(sns_subscription)

        # Defining Topic Rule properties
        action = iot.CfnTopicRule.SnsActionProperty(target_arn=self._sns_topic.topic_arn, role_arn=role.role_arn)
        action_property = iot.CfnTopicRule.ActionProperty(sns=action)

        rule_data = self._configuration["iot_rule"]
        self._iot_rule = base_iot_rule(self, action_property=action_property, **rule_data)

    def set_alarms(self):
        """

        :return:
        """
        if isinstance(self._configuration["topic"].get("alarms"), list) is True:
            sns_alarms = list()
            for alarm_definition in self._configuration["topic"].get("alarms"):
                sns_alarms.append(
                    base_alarm(
                        self, resource_name=self._configuration["topic"]["topic_name"], base_resource=self._sns_topic, **alarm_definition
                    )
                )

        for lambda_function_data, lambda_function_definition in zip(self._configuration["lambda_handlers"], self._lambda_functions):
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

        :return:
        """
        return self._configuration

    @property
    def sns_topic(self):
        """

        :return:
        """
        return self._sns_topic

    @property
    def lambda_function(self):
        """

        :return:
        """
        return self._lambda_function

    @property
    def iot_rule(self):
        """

        :return:
        """
        return self._iot_rule
