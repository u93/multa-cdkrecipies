import traceback

from aws_cdk import (
    core,
    aws_iam as iam,
    aws_iot as iot,
    aws_lambda as lambda_,
    aws_sns as sns,
    aws_sns_subscriptions as sns_subs,
)

from .utils import SNS_CONFIG_SCHEMA, validate_configuration, WrongRuntimePassed


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
        super().__init__(scope, id, **kwargs)
        self.prefix = prefix
        self.environment_ = environment

        # Validating that the payload passed is correct
        validate_configuration(configuration_schema=SNS_CONFIG_SCHEMA, configuration_received=configuration)

        # Defining SNS Topic
        sns_name = self.prefix + configuration["topic_name"] + "_" + "topic" + "_" + self.environment_
        iam_role_name = self.prefix + configuration["topic_name"] + "_" + "topic_role" + "_" + self.environment_
        iam_policy_name = self.prefix + configuration["topic_name"] + "_" + "topic_policy" + "_" + self.environment_

        self._sns_topic = sns.Topic(self, id=sns_name, topic_name=sns_name, display_name=sns_name)

        # Defining IAM Role
        # Defining Service Principal
        principal = iam.ServicePrincipal(service="iot.amazonaws.com")

        # Defining IAM Role
        role = iam.Role(self, id=iam_role_name, role_name=iam_role_name, assumed_by=principal)

        # Defining Policy Statement, Policy and Attaching to Role
        policy_statements = iam.PolicyStatement(actions=["SNS:Publish"], resources=[self._sns_topic.topic_arn])
        policy = iam.Policy(self, id=iam_policy_name, policy_name=iam_policy_name, statements=[policy_statements])
        policy.attach_to_role(role=role)

        # Validating Lambda Function Runtime
        function_data = configuration["lambda_handler"]
        try:
            function_runtime = getattr(lambda_.Runtime, function_data["runtime"])
        except Exception:
            raise WrongRuntimePassed(
                detail=f"Wrong function runtime {function_data['runtime']} specified", tb=traceback.format_exc()
            )

        # Defining Lambda function
        self._lambda_function = lambda_.Function(
            self,
            id=self.prefix + "_" + function_data["lambda_name"] + "_" + "lambda" + "_" + self.environment_,
            function_name=self.prefix + "_" + function_data["lambda_name"] + "_" + "lambda" + "_" + self.environment_,
            code=lambda_.Code.from_asset(path=function_data["code_path"]),
            handler=function_data["handler"],
            runtime=function_runtime,
            # layers=layers,
            description=function_data.get("description"),
            tracing=lambda_.Tracing.ACTIVE,
            environment=function_data.get("environment_vars"),
            timeout=core.Duration.seconds(function_data.get("timeout")),
            reserved_concurrent_executions=function_data.get("reserved_concurrent_executions"),
        )

        # Defining Lambda Function IAM policies to access other services
        self.iam_policies = list()
        for iam_actions in configuration["iam_actions"]:
            self.iam_policies.append(iam_actions)

        policy_statement = iam.PolicyStatement(actions=self.iam_policies, resources=["*"])
        self._lambda_function.add_to_role_policy(statement=policy_statement)

        # Defining the Lambda subscription to the specified SNS Topic in cdk.json file.
        sns_subscription = sns_subs.LambdaSubscription(fn=self._lambda_function)
        self._sns_topic.add_subscription(sns_subscription)

        # Defining Topic Rule properties
        action = iot.CfnTopicRule.SnsActionProperty(target_arn=self._sns_topic.topic_arn, role_arn=role.role_arn)
        action_property = iot.CfnTopicRule.ActionProperty(sns=action)

        rule_data = configuration["iot_rule"]
        rule_payload = iot.CfnTopicRule.TopicRulePayloadProperty(
            actions=[action_property],
            rule_disabled=rule_data["rule_disabled"],
            sql=rule_data["sql"],
            aws_iot_sql_version=rule_data["aws_iot_sql_version"],
            description=rule_data.get("description"),
        )

        # Defining AWS IoT Rule
        rule_name = self.prefix + "_" + rule_data["rule_name"] + "_" + "topic_rule" + "_" + self.environment_
        self._iot_rule = iot.CfnTopicRule(self, id=rule_name, rule_name=rule_name, topic_rule_payload=rule_payload)

    @property
    def sns_topic(self):
        return self._sns_topic

    @property
    def lambda_function(self):
        return self._lambda_function

    @property
    def iot_rule(self):
        return self._iot_rule
