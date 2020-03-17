from copy import deepcopy
import traceback

from aws_cdk import (
    core,
    aws_cloudwatch as cloudwatch,
    aws_iam as iam,
    aws_iot as iot,
    aws_lambda as lambda_,
    aws_lambda_event_sources as lambda_sources,
)
from .common import base_queue_cdk
from .settings import DEFAULT_LAMBDA_CODE_PATH, DEFAULT_LAMBDA_CODE_PATH_EXISTS
from .utils import IOT_SQS_CONFIG_SCHEMA, validate_configuration, WrongRuntimePassed


class AwsIotRulesSqsPipes(core.Construct):
    """
    AWS CDK Construct that defines a pipe where a Rules captures an MQTT Message sent to or from AWS IoT MQTT Broker,
    then the message is sent to an SQS Queue and a Lambda function subscribed to the topic can process it and take
    proper actions. The construct takes a few inputs.

    Attributes:
        prefix (str): The prefix set on the name of each resource created in the stack. Just for organization purposes.
        environment_ (str): The environment that all resources will use. Also for organizational and testing purposes.
        _sqs_queue (object): SQS Queue representation in CDK.
        _lambda_function (object): Lambda Function representation in CDK.
        _iot_rule (object): IoT Topic Rule representation in CDK.

    """

    def __init__(self, scope: core.Construct, id: str, *, prefix: str, environment: str, configuration, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.prefix = prefix
        self.environment_ = environment
        self.configuration = configuration
        validate_configuration(configuration_schema=IOT_SQS_CONFIG_SCHEMA, configuration_received=self.configuration)

        # Defining SQS Queue
        queue_data = deepcopy(self.configuration["queue"])
        iam_role_name = self.prefix + "_" + queue_data["queue_name"] + "_queue_role_" + self.environment_
        iam_policy_name = self.prefix + "_" + queue_data["queue_name"] + "_queue_policy_" + self.environment_
        queue_data["queue_name"] = self.prefix + "_" + queue_data["queue_name"] + "_queue_" + self.environment_

        self._sqs_queue = base_queue_cdk(construct=self, **queue_data)

        # Defining IAM Role
        # Defining Service Principal
        principal = iam.ServicePrincipal(service="iot.amazonaws.com")

        # Defining IAM Role
        role = iam.Role(self, id=iam_role_name, role_name=iam_role_name, assumed_by=principal)

        # Defining Policy Statement, Policy and Attaching to Role
        policy_statements = iam.PolicyStatement(actions=["sqs:SendMessage"], resources=[self._sqs_queue.queue_arn])
        policy = iam.Policy(self, id=iam_policy_name, policy_name=iam_policy_name, statements=[policy_statements])
        policy.attach_to_role(role=role)

        # Validating Lambda Function Runtime
        functions_data = self.configuration["lambda_handlers"]
        self._lambda_functions = list()
        for lambda_function in functions_data:
            try:
                function_runtime = getattr(lambda_.Runtime, lambda_function["runtime"])
            except Exception:
                raise WrongRuntimePassed(detail=f"Wrong function runtime {lambda_function['runtime']} specified", tb=traceback.format_exc())

            obtainer_code_path = lambda_function.get("code_path")
            if obtainer_code_path is not None:
                code_path = obtainer_code_path
            elif obtainer_code_path is None and DEFAULT_LAMBDA_CODE_PATH_EXISTS is True:
                code_path = DEFAULT_LAMBDA_CODE_PATH
            else:
                raise RuntimeError(f"Code path for Lambda Function {lambda_function['lambda_name']} is not valid!")

            # Defining Lambda function
            _lambda_function = lambda_.Function(
                self,
                id=self.prefix + "_" + lambda_function["lambda_name"] + "_lambda_" + self.environment_,
                function_name=self.prefix + "_" + lambda_function["lambda_name"] + "_lambda_" + self.environment_,
                code=lambda_.Code.from_asset(path=code_path),
                handler=lambda_function["handler"],
                runtime=function_runtime,
                layers=None,
                description=lambda_function.get("description"),
                tracing=lambda_.Tracing.ACTIVE,
                environment=lambda_function.get("environment_vars"),
                timeout=core.Duration.seconds(lambda_function.get("timeout")),
                reserved_concurrent_executions=lambda_function.get("reserved_concurrent_executions"),
            )

            # Defining the Lambda subscription to the specified SQS Queue in cdk.json file.
            _lambda_function.add_event_source(lambda_sources.SqsEventSource(queue=self._sqs_queue, batch_size=10))

            # Defining Lambda Function IAM policies to access other services
            self.iam_policies = list()
            for iam_actions in self.configuration["iam_actions"]:
                self.iam_policies.append(iam_actions)

            policy_statement = iam.PolicyStatement(actions=self.iam_policies, resources=["*"])
            _lambda_function.add_to_role_policy(statement=policy_statement)

            self._lambda_functions.append(_lambda_function)

        # Defining Topic Rule properties
        action = iot.CfnTopicRule.SqsActionProperty(queue_url=self._sqs_queue.queue_url, role_arn=role.role_arn)
        action_property = iot.CfnTopicRule.ActionProperty(sqs=action)

        rule_data = self.configuration["iot_rule"]
        rule_payload = iot.CfnTopicRule.TopicRulePayloadProperty(
            actions=[action_property],
            rule_disabled=rule_data["rule_disabled"],
            sql=rule_data["sql"],
            aws_iot_sql_version=rule_data["aws_iot_sql_version"],
            description=rule_data.get("description"),
        )

        # Defining AWS IoT Rule
        rule_name = self.prefix + "_" + rule_data["rule_name"] + "_" + self.environment_
        self._iot_rule = iot.CfnTopicRule(self, id=rule_name, rule_name=rule_name, topic_rule_payload=rule_payload)

    def set_alarms(self):
        if isinstance(self.configuration["queue"].get("alarms"), list) is True:
            sqs_alarms = list()
            for alarm_definition in self.configuration["queue"].get("alarms"):
                try:
                    sqs_alarms.append(
                        cloudwatch.Alarm(
                            self,
                            id="iot_sqs_lambda_" + self.configuration["queue"]["queue_name"] + "_" + alarm_definition["name"],
                            alarm_name="iot_sqs_lambda_" + self.configuration["queue"]["queue_name"] + "_" + alarm_definition["name"],
                            metric=self._sqs_queue.metric(alarm_definition["name"]),
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
                                id="iot_sqs_lambda_" + lambda_function_data["lambda_name"] + "_" + alarm_definition["name"],
                                alarm_name="iot_sqs_lambda_" + lambda_function_data["lambda_name"] + "_" + alarm_definition["name"],
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
    def sqs_queue(self):
        return self._sqs_queue

    @property
    def lambda_functions(self):
        return self._lambda_functions

    @property
    def iot_rule(self):
        return self._iot_rule
