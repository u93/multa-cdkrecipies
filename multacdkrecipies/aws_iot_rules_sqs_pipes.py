from aws_cdk import (
    core,
    aws_iam as iam,
    aws_iot as iot,
    aws_lambda as lambda_,
    aws_sqs as sqs,
)
from schema import Schema, And, Use, Optional, SchemaError

SQS_CONFIG_SCHEMA = Schema(
    {
        "queue_name": And(Use(str)),
        "lambda_handler": {
            "lambda_name": And(Use(str)),
            "description": And(Use(str)),
            "code_path": And(Use(str)),
            "runtime": And(Use(str)),
            "handler": And(Use(str)),
            "timeout": And(Use(int)),
            "reserved_concurrent_executions": And(Use(int)),
            Optional("environment_vars"): And(Use(dict)),
        },
        "iam_actions": And(Use(list)),
        "iot_rule": {
            "rule_name": And(Use(str)),
            "description": And(Use(str)),
            "rule_disabled": And(Use(bool)),
            "sql": And(Use(str)),
            "aws_iot_sql_version": And(Use(str)),
        },
    }
)


class AwsIotRulesSqsPipes(core.Construct):
    def __init__(self, scope: core.Construct, id: str, *, prefix: str, environment: str, configuration, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.prefix = prefix
        self.environment_ = environment
        valid_config = self.validate_configuration(
            configuration_schema=SQS_CONFIG_SCHEMA, configuration_received=configuration
        )
        if not valid_config:
            raise RuntimeError("Improper configuration passed to AwsIotRulesSnsPipes CDK Cons")

        sqs_name = self.prefix + configuration["queue_name"] + "_" + "topic" + "_" + self.environment_
        iam_role_name = self.prefix + configuration["queue_name"] + "_" + "topic_role" + "_" + self.environment_
        iam_policy_name = self.prefix + configuration["queue_name"] + "_" + "topic_policy" + "_" + self.environment_

        # Defining SNS Topic
        self._sqs_queue = sqs.Queue(self, id=sqs_name, queue_name=sqs_name)

        # Defining IAM Role
        # Defining Service Principal
        principal = iam.ServicePrincipal(service="iot.amazonaws.com")

        # Defining IAM Role
        role = iam.Role(self, id=iam_role_name, role_name=iam_role_name, assumed_by=principal)

        # Defining Policy Statement, Policy and Attaching to Role
        policy_statements = iam.PolicyStatement(actions=["sqs:SendMessage"], resources=[self._sqs_queue.queue_arn])
        policy = iam.Policy(self, id=iam_policy_name, policy_name=iam_policy_name, statements=[policy_statements])
        policy.attach_to_role(role=role)

        function_data = configuration["lambda_handler"]
        try:
            function_runtime = getattr(lambda_.Runtime, function_data["runtime"])
        except Exception as e:
            raise RuntimeError(f"Wrong function runtime {function_data['runtime']} specified")

        self._lambda_function = lambda_.Function(
            self,
            id=self.prefix + "_" + function_data["lambda_name"] + "_" + self.environment_,
            function_name=self.prefix + "_" + function_data["lambda_name"] + "_" + self.environment_,
            code=lambda_.Code.from_asset(path=function_data["code_path"]),
            handler=function_data["handler"],
            runtime=function_runtime,
            # layers=layers,
            description=function_data["description"],
            tracing=lambda_.Tracing.ACTIVE,
            environment=function_data.get("environment_vars"),
            timeout=core.Duration.seconds(function_data["timeout"]),
            reserved_concurrent_executions=function_data["reserved_concurrent_executions"],
        )

        self.iam_policies = list()
        for iam_actions in configuration["iam_actions"]:
            self.iam_policies.append(iam_actions)

        policy_statement = iam.PolicyStatement(actions=self.iam_policies, resources=["*"])
        self._lambda_function.add_to_role_policy(statement=policy_statement)

        action = iot.CfnTopicRule.SqsActionProperty(queue_url=self._sqs_queue.queue_url, role_arn=role.role_arn)
        action_property = iot.CfnTopicRule.ActionProperty(sqs=action)

        rule_data = configuration["iot_rule"]
        rule_payload = iot.CfnTopicRule.TopicRulePayloadProperty(
            actions=[action_property],
            rule_disabled=rule_data["rule_disabled"],
            sql=rule_data["sql"],
            aws_iot_sql_version=rule_data["aws_iot_sql_version"],
            description=rule_data["description"],
        )

        # Defining AWS IoT Rules
        rule_name = self.prefix + "_" + rule_data["rule_name"] + "_" + self.environment_
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

    @staticmethod
    def validate_configuration(configuration_schema, configuration_received):
        try:
            configuration_schema.validate(configuration_received)
            return True
        except SchemaError:
            return False
