import traceback

from aws_cdk import (
    core,
    aws_apigateway as api_gateway,
    aws_certificatemanager as cert_manager,
    aws_cloudwatch as cloudwatch,
    aws_iam as iam,
    aws_lambda as lambda_,
)

from .settings import DEFAULT_LAMBDA_CODE_PATH, DEFAULT_LAMBDA_CODE_PATH_EXISTS
from .utils import APIGATEWAY_LAMBDA_SIMPLE_WEB_SERVICE_SCHEMA, validate_configuration, WrongRuntimePassed


class AwsApiGatewayLambdaSWS(core.Construct):
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
        validate_configuration(configuration_schema=APIGATEWAY_LAMBDA_SIMPLE_WEB_SERVICE_SCHEMA, configuration_received=self.configuration)
        api_configuration = self.configuration["api"]

        # Define Lambda Authorizers
        lambda_authorizers = api_configuration["lambda_authorizer"]
        self._authorizer_lambda_functions = list()

        # Define IN-ACCOUNT Lambda Authorizers
        in_account_lambda_authorizer = lambda_authorizers.get("imported")
        if in_account_lambda_authorizer is not None:
            self._authorizer_lambda_functions.append(lambda_.Function.from_function_arn(in_account_lambda_authorizer["lambda_arn"]))

        # Define NEW-FUNCTION Lambda Authorizers
        defined_lambda_authorizer = lambda_authorizers.get("origin")
        if defined_lambda_authorizer is not None:
            try:
                function_runtime = getattr(lambda_.Runtime, defined_lambda_authorizer["runtime"])
            except Exception:
                raise WrongRuntimePassed(
                    detail=f"Wrong function runtime {defined_lambda_authorizer['runtime']} specified", tb=traceback.format_exc()
                )

            obtainer_code_path = defined_lambda_authorizer.get("code_path")
            if obtainer_code_path is not None:
                code_path = obtainer_code_path
            elif obtainer_code_path is None and DEFAULT_LAMBDA_CODE_PATH_EXISTS is True:
                code_path = DEFAULT_LAMBDA_CODE_PATH
            else:
                raise RuntimeError(f"Code path for Lambda Function {defined_lambda_authorizer['lambda_name']} is not valid!")

            # Defining Lambda function
            _lambda_function = lambda_.Function(
                self,
                id=self.prefix + "_" + defined_lambda_authorizer["lambda_name"] + "_auth_" + self.environment_,
                function_name=self.prefix + "_" + defined_lambda_authorizer["lambda_name"] + "_auth_" + self.environment_,
                code=lambda_.Code.from_asset(path=code_path),
                handler=defined_lambda_authorizer["handler"],
                runtime=function_runtime,
                layers=None,
                description=defined_lambda_authorizer.get("description"),
                tracing=lambda_.Tracing.ACTIVE,
                environment=defined_lambda_authorizer.get("environment_vars"),
                timeout=core.Duration.seconds(defined_lambda_authorizer.get("timeout")),
                reserved_concurrent_executions=defined_lambda_authorizer.get("reserved_concurrent_executions"),
            )
            self._authorizer_lambda_functions.append(_lambda_function)

            # Defining Lambda Function IAM policies to access other services
            self.auth_iam_policies = list()
            for iam_actions in api_configuration["lambda_authorizer"]["origin"]["iam_actions"]:
                self.auth_iam_policies.append(iam_actions)

            for added_authorizer_function in self._authorizer_lambda_functions:
                policy_statement = iam.PolicyStatement(actions=self.auth_iam_policies, resources=["*"])
                added_authorizer_function.add_to_role_policy(statement=policy_statement)

        # Define API Gateway Lambda Handler
        lambda_handlers = api_configuration["resource"]["handler"]
        self._handler_lambda_functions = list()

        # Define imported Lambda Handler
        imported_lambda_handler = lambda_handlers.get("imported")
        if imported_lambda_handler is not None:
            self._handler_lambda_functions.append(lambda_.Function.from_function_arn(imported_lambda_handler["lambda_arn"]))

        defined_lambda_handler = lambda_handlers.get("origin")
        if defined_lambda_handler is not None:
            try:
                function_runtime = getattr(lambda_.Runtime, defined_lambda_handler["runtime"])
            except Exception:
                raise WrongRuntimePassed(
                    detail=f"Wrong function runtime {defined_lambda_handler['runtime']} specified", tb=traceback.format_exc()
                )

            obtainer_code_path = defined_lambda_handler.get("code_path")
            if obtainer_code_path is not None:
                code_path = obtainer_code_path
            elif obtainer_code_path is None and DEFAULT_LAMBDA_CODE_PATH_EXISTS is True:
                code_path = DEFAULT_LAMBDA_CODE_PATH
            else:
                raise RuntimeError(f"Code path for Lambda Function {defined_lambda_handler['lambda_name']} is not valid!")

            # Defining Lambda function
            _lambda_function = lambda_.Function(
                self,
                id=self.prefix + "_" + defined_lambda_handler["lambda_name"] + "_handler_" + self.environment_,
                function_name=self.prefix + "_" + defined_lambda_handler["lambda_name"] + "_handler_" + self.environment_,
                code=lambda_.Code.from_asset(path=code_path),
                handler=defined_lambda_handler["handler"],
                runtime=function_runtime,
                layers=None,
                description=defined_lambda_handler.get("description"),
                tracing=lambda_.Tracing.ACTIVE,
                environment=defined_lambda_handler.get("environment_vars"),
                timeout=core.Duration.seconds(defined_lambda_handler.get("timeout")),
                reserved_concurrent_executions=defined_lambda_handler.get("reserved_concurrent_executions"),
            )
            self._handler_lambda_functions.append(_lambda_function)

            # Defining Lambda Function IAM policies to access other services
            self.handler_iam_policies = list()
            for iam_actions in api_configuration["resource"]["handler"]["origin"]["iam_actions"]:
                self.handler_iam_policies.append(iam_actions)

            for added_authorizer_function in self._handler_lambda_functions:
                policy_statement = iam.PolicyStatement(actions=self.handler_iam_policies, resources=["*"])
                added_authorizer_function.add_to_role_policy(statement=policy_statement)

        # Define Gateway
        try:
            desired_handler = self._handler_lambda_functions[0]
        except IndexError:
            print("Unable to find defined Lambda Handler! Please verify configuration payload...")
            raise RuntimeError("Unable to find defined Lambda Handler! Please verify configuration payload...")

        try:
            desired_auth_handler = self._authorizer_lambda_functions[0]
        except IndexError:
            print("Unable to find defined Auth Lambda Handler! Please verify configuration payload...")
            raise RuntimeError("Unable to find defined Auth Lambda Handler! Please verify configuration payload...")

        custom_domain = api_configuration["resource"].get("custom_domain")
        if custom_domain is not None:
            domain_name = custom_domain["domain_name"]
            certificate_arn = custom_domain["certificate_arn"]
            domain_options = api_gateway.DomainNameOptions(
                certificate=cert_manager.Certificate.from_certificate_arn(certificate_arn), domain_name=domain_name
            )
        else:
            domain_options = None

        gateway = api_gateway.LambdaRestApi(
            self,
            id=api_configuration["apigateway_name"],
            rest_api_name=api_configuration["apigateway_name"],
            description=api_configuration["apigateway_description"],
            domain_name=domain_options,
            handler=desired_handler,
            proxy=False,
        )

        # Define Gateway Token Authorizer
        authorizer_name = api_configuration["apigateway_name"] + "_" + "authorizer"
        gateway_authorizer = api_gateway.TokenAuthorizer(
            self, id=authorizer_name, authorizer_name=authorizer_name, handler=desired_auth_handler
        )

        # Define Gateway Resource and Methods
        resource = gateway.root.add_resource(api_configuration["resource"]["name"])
        gateway_methods = api_configuration["resource"]["methods"]
        for method in gateway_methods:
            resource.add_method(http_method=method, authorizer=gateway_authorizer)

        allowed_origins = api_configuration["resource"].get("allowed_origins")
        if allowed_origins is not None:
            resource.add_cors_preflight(allow_origins=allowed_origins, allow_methods=gateway_methods)
