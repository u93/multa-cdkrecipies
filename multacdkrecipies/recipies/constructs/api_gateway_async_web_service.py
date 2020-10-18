import traceback

from aws_cdk import core

from multacdkrecipies.common import base_bucket, base_lambda_function
from multacdkrecipies.recipies.settings import DEFAULT_LAMBDA_CODE_PATH, DEFAULT_LAMBDA_CODE_PATH_EXISTS
from multacdkrecipies.recipies.utils import (
    APIGATEWAY_ASYNC_WEB_SERVICE_SCHEMA,
    validate_configuration,
    WrongRuntimePassed,
)


class AwsApiGatewayLambdaPipesAsync(core.Construct):
    """
    AWS CDK Construct that defines a Simple Web Service formed by a RestAPI that has a Lambda Authorizer function
    that can be imported or created (if both are passed as configuration, the first of the imported has higher
    priority compared to the new one)... Also has a Lambda handler function that will respond to at least one
    method (GET, POST) that can be imported or created (if both are passed as configuration, the first of the imported has higher
    priority compared to the new one)... Custom domain with certificate configuration can also be passed to the RestAPI
    with also the possibility to configure CORS for the API.
    """

    def __init__(self, scope: core.Construct, id: str, *, prefix: str, environment: str, configuration, **kwargs):
        """
        :param scope: Stack class, used by CDK.
        :param id: ID of the construct, used by CDK.
        :param prefix: Prefix of the construct, used for naming purposes.
        :param environment: Environment of the construct, used for naming purposes.
        :param configuration: Configuration of the construct. In this case APIGATEWAY_LAMBDA_SIMPLE_WEB_SERVICE_SCHEMA.
        :param kwargs: Other parameters that could be used by the construct.
        """
        super().__init__(scope, id, **kwargs)
        self.prefix = prefix
        self.environment_ = environment
        self._configuration = configuration

        # Validating that the payload passed is correct
        validate_configuration(
            configuration_schema=APIGATEWAY_ASYNC_WEB_SERVICE_SCHEMA, configuration_received=self._configuration
        )
        # Define S3 Buckets Cluster
        if isinstance(self._configuration.get("buckets"), list):
            self._s3_buckets = [base_bucket(self, **bucket) for bucket in self._configuration["buckets"]]

        api_configuration = self._configuration["api"]

        # Define Lambda Authorizer Function
        authorizer_functions = api_configuration.get("authorizer_function")
        self._authorizer_function = None
        if authorizer_functions is not None:
            if authorizer_functions.get("imported") is not None:
                self._authorizer_function = lambda_.Function.from_function_arn(
                    self,
                    id=authorizer_functions.get("imported").get("identifier"),
                    function_arn=authorizer_functions.get("imported").get("arn"),
                )
            elif authorizer_functions.get("origin") is not None:
                self._authorizer_function = base_lambda_function(self, **authorizer_functions.get("origin"))

        # Define NEW-FUNCTION Lambda Authorizers
        for lambda_function in authorizer_functions["origin"]:
            try:
                function_runtime = getattr(lambda_.Runtime, lambda_function["runtime"])
            except Exception:
                raise WrongRuntimePassed(
                    detail=f"Wrong function runtime {lambda_function['runtime']} specified", tb=traceback.format_exc()
                )

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
