import traceback

from aws_cdk import (
    core,
    aws_apigateway as api_gateway,
    aws_cloudwatch as cloudwatch,
    aws_iam as iam,
    aws_lambda as lambda_,
)

from .settings import DEFAULT_LAMBDA_CODE_PATH, DEFAULT_LAMBDA_CODE_PATH_EXISTS
from .utils import APIGATEWAY_LAMBDA_SCHEMA, validate_configuration, WrongRuntimePassed


class AwsApiGatewayLambdaPipesAsync(core.Construct):
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
        self.configuration = configuration
        api_configuration = self.configuration["api"]

        # Validating that the payload passed is correct
        validate_configuration(configuration_schema=APIGATEWAY_LAMBDA_SCHEMA, configuration_received=self.configuration)

        # Define Lambda Authorizers
        lambda_authorizers = api_configuration["lambda_authorizer"]
        self._authorizer_lambda_functions = list()

        # Define IN-ACCOUNT Lambda Authorizers
        for lambda_function in lambda_authorizers["imported"]:
            self._authorizer_lambda_functions.append(lambda_.Function.from_function_arn(lambda_function["lambda_arn"]))

        # Define NEW-FUNCTION Lambda Authorizers
        for lambda_function in lambda_authorizers["origin"]:
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

            # Defining Lambda Function IAM policies to access other services
            self.iam_policies = list()
            for iam_actions in configuration["iam_actions"]:
                self.iam_policies.append(iam_actions)

            policy_statement = iam.PolicyStatement(actions=self.iam_policies, resources=["*"])
            _lambda_function.add_to_role_policy(statement=policy_statement)
            self._authorizer_lambda_functions.append(_lambda_function)

        # Define API Methods
