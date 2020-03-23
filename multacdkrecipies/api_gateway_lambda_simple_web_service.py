from aws_cdk import (
    core,
    aws_apigateway as api_gateway,
    aws_certificatemanager as cert_manager,
    aws_lambda as lambda_,
)
from .common import base_alarm, base_lambda_function
from .utils import APIGATEWAY_LAMBDA_SIMPLE_WEB_SERVICE_SCHEMA, validate_configuration


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
        self._configuration = configuration

        # Validating that the payload passed is correct
        validate_configuration(configuration_schema=APIGATEWAY_LAMBDA_SIMPLE_WEB_SERVICE_SCHEMA, configuration_received=self._configuration)
        api_configuration = self._configuration["api"]

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
            _lambda_function = base_lambda_function(self, **defined_lambda_authorizer)
            self._authorizer_lambda_functions.append(_lambda_function)

        # Define API Gateway Lambda Handler
        lambda_handlers = api_configuration["resource"]["handler"]
        self._handler_lambda_functions = list()

        # Define imported Lambda Handler
        imported_lambda_handler = lambda_handlers.get("imported")
        if imported_lambda_handler is not None:
            self._handler_lambda_functions.append(lambda_.Function.from_function_arn(imported_lambda_handler["lambda_arn"]))

        defined_lambda_handler = lambda_handlers.get("origin")
        if defined_lambda_handler is not None:
            _lambda_function = base_lambda_function(self, **defined_lambda_handler)
            self._handler_lambda_functions.append(_lambda_function)

        # Define Gateway
        try:
            desired_auth_handler = self._authorizer_lambda_functions[0]
        except IndexError:
            print("Unable to find defined Auth Lambda Handler! Please verify configuration payload...")
            raise RuntimeError("Unable to find defined Auth Lambda Handler! Please verify configuration payload...")

        try:
            desired_handler = self._handler_lambda_functions[0]
        except IndexError:
            print("Unable to find defined Lambda Handler! Please verify configuration payload...")
            raise RuntimeError("Unable to find defined Lambda Handler! Please verify configuration payload...")

        custom_domain = api_configuration["resource"].get("custom_domain")
        if custom_domain is not None:
            domain_name = custom_domain["domain_name"]
            certificate_arn = custom_domain["certificate_arn"]
            domain_options = api_gateway.DomainNameOptions(
                certificate=cert_manager.Certificate.from_certificate_arn(certificate_arn), domain_name=domain_name
            )
        else:
            domain_options = None

        self._lambda_rest_api = api_gateway.LambdaRestApi(
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
        resource = self._lambda_rest_api.root.add_resource(api_configuration["resource"]["name"])
        gateway_methods = api_configuration["resource"]["methods"]
        for method in gateway_methods:
            resource.add_method(http_method=method, authorizer=gateway_authorizer)

        allowed_origins = api_configuration["resource"].get("allowed_origins")
        if allowed_origins is not None:
            resource.add_cors_preflight(allow_origins=allowed_origins, allow_methods=gateway_methods)

    def set_alarms(self):
        if isinstance(self._configuration["api"]["lambda_authorizer"].get("alarms"), list) is True:
            authorizer_alarms = list()
            for alarm_definition in self._configuration["api"]["lambda_authorizer"].get("alarms"):
                authorizer_alarms.append(
                    base_alarm(
                        self,
                        resource_name="lambda_authorizer",
                        base_resource=self._authorizer_lambda_functions[0],
                        **alarm_definition
                    )
                )

        if isinstance(self._configuration["api"]["resource"]["handler"].get("alarms"), list) is True:
            authorizer_alarms = list()
            for alarm_definition in self._configuration["api"]["resource"]["handler"].get("alarms"):
                authorizer_alarms.append(
                    base_alarm(
                        self,
                        resource_name="lambda_api_handler",
                        base_resource=self._handler_lambda_functions[0],
                        **alarm_definition
                    )
                )

    @property
    def lambda_rest_api(self):
        return self._lambda_rest_api

    @property
    def lambda_authorizer_function(self):
        return self._authorizer_lambda_functions[0]

    @property
    def lambda_handler_function(self):
        return self._handler_lambda_functions[0]

