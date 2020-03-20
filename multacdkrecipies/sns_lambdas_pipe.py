import traceback

from aws_cdk import (
    core,
    aws_cloudwatch as cloudwatch,
    aws_sns as sns,
    aws_sns_subscriptions as sns_subs,
)
from .common import base_lambda_function
from .utils import SNS_CONFIG_SCHEMA, validate_configuration


class AwsSnsPipes(core.Construct):
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
        super().__init__(scope, id, **kwargs)
        self.prefix = prefix
        self.environment_ = environment
        self.configuration = configuration

        # Validating that the payload passed is correct
        validate_configuration(configuration_schema=SNS_CONFIG_SCHEMA, configuration_received=self.configuration)

        # Defining SNS Topic
        topic_data = self.configuration["topic"]
        sns_name = self.prefix + "_" + topic_data["topic_name"] + "_" + "topic" + "_" + self.environment_
        # iam_role_name = self.prefix + "_" + topic_data["topic_name"] + "_" + "topic_role" + "_" + self.environment_
        # iam_policy_name = self.prefix + "_" + topic_data["topic_name"] + "_" + "topic_policy" + "_" + self.environment_

        self._sns_topic = sns.Topic(self, id=sns_name, topic_name=sns_name, display_name=sns_name)

        # # Defining IAM Role
        # # Defining Service Principal
        # principal = iam.ServicePrincipal(service="iot.amazonaws.com")
        #
        # # Defining IAM Role
        # role = iam.Role(self, id=iam_role_name, role_name=iam_role_name, assumed_by=principal)
        #
        # # Defining Policy Statement, Policy and Attaching to Role
        # policy_statements = iam.PolicyStatement(actions=["SNS:Publish"], resources=[self._sns_topic.topic_arn])
        # policy = iam.Policy(self, id=iam_policy_name, policy_name=iam_policy_name, statements=[policy_statements])
        # policy.attach_to_role(role=role)

        # Validating Lambda Function Runtime
        functions_data = self.configuration["lambda_handlers"]
        self._lambda_functions = list()
        for lambda_function in functions_data:
            _lambda_function = base_lambda_function(self, **lambda_function)
            self._lambda_functions.append(_lambda_function)

            # Defining the Lambda subscription to the specified SNS Topic in cdk.json file.
            sns_subscription = sns_subs.LambdaSubscription(fn=_lambda_function)
            self._sns_topic.add_subscription(sns_subscription)

    def set_alarms(self):
        if isinstance(self.configuration["topic"].get("alarms"), list) is True:
            sns_alarms = list()
            for alarm_definition in self.configuration["topic"].get("alarms"):
                try:
                    sns_alarms.append(
                        cloudwatch.Alarm(
                            self,
                            id="iot_sns_lambda_" + self.configuration["topic"]["topic_name"] + "_" + alarm_definition["name"],
                            alarm_name="iot_sns_lambda_" + self.configuration["topic"]["topic_name"] + "_" + alarm_definition["name"],
                            metric=self._sns_topic.metric(alarm_definition["name"]),  # metric_number_of_notifications_failed
                            threshold=alarm_definition["number"],
                            evaluation_periods=alarm_definition["periods"],
                            datapoints_to_alarm=alarm_definition["points"],
                            actions_enabled=alarm_definition["actions"],
                        )
                    )
                except Exception:
                    print(traceback.format_exc())

        for lambda_function_data, lambda_function_definition in zip(self.configuration["lambda_handlers"], self._lambda_functions):
            if isinstance(lambda_function_data.get("alarms"), list) is True:
                lambda_alarms = list()
                for alarm_definition in lambda_function_data.get("alarms"):
                    try:
                        lambda_alarms.append(
                            cloudwatch.Alarm(
                                self,
                                id="iot_sqs_lambda" + "_" + lambda_function_data["lambda_name"] + "_" + alarm_definition["name"],
                                alarm_name="iot_sqs_lambda" + "_" + lambda_function_data["lambda_name"] + "_" + alarm_definition["name"],
                                metric=lambda_function_definition.metric(alarm_definition["name"]),
                                threshold=alarm_definition["number"],
                                evaluation_periods=alarm_definition["periods"],
                                datapoints_to_alarm=alarm_definition["points"],
                                actions_enabled=alarm_definition["actions"],
                            )
                        )
                    except Exception:
                        print(traceback.format_exc())

    @property
    def sns_topic(self):
        return self._sns_topic

    @property
    def lambda_function(self):
        return self._lambda_function
