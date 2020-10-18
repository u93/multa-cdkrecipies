from aws_cdk import (
    core,
    aws_apigateway as api_gateway,
    aws_certificatemanager as cert_manager,
    aws_lambda as lambda_,
)
from multacdkrecipies.common import base_bucket, base_alarm, base_lambda_function
from multacdkrecipies.recipies.utils import APIGATEWAY_FAN_OUT_WEB_SERVICE_SCHEMA, validate_configuration


class AwsApiGatewayLambdaFanOutBE(core.Construct):
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
        :param configuration: Configuration of the construct. In this case APIGATEWAY_FAN_OUT_SCHEMA.
        :param kwargs: Other parameters that could be used by the construct.
        """
        super().__init__(scope, id, **kwargs)
        self.prefix = prefix
        self.environment_ = environment
        self._configuration = configuration

        # Validating that the payload passed is correct
        validate_configuration(
            configuration_schema=APIGATEWAY_FAN_OUT_WEB_SERVICE_SCHEMA, configuration_received=self._configuration
        )
        # Define S3 Buckets Cluster
        if isinstance(self._configuration.get("buckets"), list):
            self._s3_buckets = [base_bucket(self, **bucket) for bucket in self._configuration["buckets"]]

        api_configuration = self._configuration["api"]
        api_gateway_name = self.prefix + "_" + api_configuration["apigateway_name"] + "_" + self.environment_
        api_gateway_name_description = api_configuration.get("apigateway_description")

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

        # Define API Gateway Authorizer
        gateway_authorizer = None
        if self._authorizer_function is not None:
            # Define Gateway Token Authorizer
            authorizer_name = api_configuration["apigateway_name"] + "_" + "authorizer"
            gateway_authorizer = api_gateway.TokenAuthorizer(
                self, id=authorizer_name, authorizer_name=authorizer_name, handler=self._authorizer_function
            )

        # Defining Custom Domain
        domain_options = None
        custom_domain = api_configuration["settings"].get("custom_domain")
        if custom_domain is not None:
            domain_name = custom_domain["domain_name"]
            certificate_arn = custom_domain["certificate_arn"]
            domain_options = api_gateway.DomainNameOptions(
                certificate=cert_manager.Certificate.from_certificate_arn(self, id=domain_name, certificate_arn=certificate_arn),
                domain_name=domain_name,
            )

        # Define API Gateway Lambda Handler
        self._handler_function = base_lambda_function(self, **api_configuration["settings"]["default_handler"])

        # Validating Proxy configuration for API Gateway
        proxy_configuration = api_configuration["settings"]["proxy"]
        if proxy_configuration is False and api_configuration["settings"].get("default_http_methods") is None:
            print("Unable to check which method to use for the API! Use proxy: True or define methods...")
            raise RuntimeError

        # Defining allowed binary media types by API Gateway
        binary_media_types = api_configuration["settings"].get("default_media_types")

        # Defining CORS preflight options
        default_cors_options = None
        default_cors_configuration = api_configuration["settings"].get("default_cors_options")
        if default_cors_configuration is not None:
            default_cors_options = api_gateway.CorsOptions(
                allow_origins=default_cors_configuration["allow_origins"],
                allow_methods=["ANY"],
                status_code=default_cors_configuration["options_status_code"],
            )

        # Defining STAGE Options
        default_stage_options = None
        default_stage_configuration = api_configuration["settings"].get("default_stage_options")
        if default_stage_configuration is not None:
            logging_level = api_gateway.MethodLoggingLevel.ERROR
            logging_level_configuration = default_stage_configuration["logging_level"]
            for element in api_gateway.MethodLoggingLevel:
                if logging_level_configuration in str(element):
                    logging_level = element
            default_stage_options = api_gateway.StageOptions(
                logging_level=logging_level,
                metrics_enabled=default_stage_configuration["metrics_enabled"],
            )

        # Defining Rest API Gateway with Lambda Integration
        self._lambda_rest_api = api_gateway.LambdaRestApi(
            self,
            id=api_gateway_name,
            rest_api_name=api_gateway_name,
            description=api_gateway_name_description,
            domain_name=domain_options,
            handler=self._handler_function,
            proxy=proxy_configuration,
            binary_media_types=binary_media_types,
            default_cors_preflight_options=default_cors_options,
            cloud_watch_role=True,
            deploy_options=default_stage_options,
        )

        # Add Custom responses
        self._lambda_rest_api.add_gateway_response(
            f"{self.prefix}_4XXresponse_{self.environment_}",
            type=api_gateway.ResponseType.DEFAULT_4_XX,
            response_headers={"Access-Control-Allow-Origin": "'*'"},
        )
        self._lambda_rest_api.add_gateway_response(
            f"{self.prefix}_5XXresponse_{self.environment_}",
            type=api_gateway.ResponseType.DEFAULT_5_XX,
            response_headers={"Access-Control-Allow-Origin": "'*'"},
        )

        # Define API Gateway Root Methods
        root_methods = api_configuration["settings"].get("default_http_methods", list())
        for method in root_methods:
            self._lambda_rest_api.root.add_method(http_method=method, authorizer=gateway_authorizer)

        # Defining Resource Trees for API Gateway with Custom Integrations
        resource = api_configuration["resource"]
        resource_base = self._lambda_rest_api.root.add_resource(path_part=resource["resource_name"])
        if resource.get("handler") is not None:
            resource_base_handler = base_lambda_function(self, **resource["handler"])
            resource_integration = api_gateway.LambdaIntegration(handler=resource_base_handler)
        else:
            resource_integration = None

        for method in resource.get("methods", list):
            resource_base.add_method(http_method=method, integration=resource_integration, authorizer=gateway_authorizer)

        # Define FAN-Out Lambda functions
        self._lambda_functions = list()
        for lambda_function in self._configuration["functions"]:
            _lambda = base_lambda_function(self, **lambda_function)
            _lambda.grant_invoke(self._handler_function)
            self._lambda_functions.append(_lambda)

    def set_alarms(self):
        """
        Function that set alarms for the resources involved in the construct. Except API Gateway resource.
        :return: None
        """
        if isinstance(self._configuration["api"]["resource"]["handler"].get("alarms"), list) is True:
            authorizer_alarms = list()
            for alarm_definition in self._configuration["api"]["resource"]["handler"].get("alarms"):
                authorizer_alarms.append(
                    base_alarm(
                        self,
                        resource_name=self._configuration["api"]["resource"]["handler"]["lambda_name"],
                        base_resource=self._handler_function,
                        **alarm_definition,
                    )
                )

        function_definition_resource = zip(self._configuration["functions"], self._lambda_functions)
        function_definition_resource_list = list(function_definition_resource)
        functions_alarms = list()
        for lambda_function, resource in function_definition_resource_list:
            if isinstance(lambda_function.get("alarms"), list) is True:
                for alarm_definition in lambda_function.get("alarms"):
                    functions_alarms.append(
                        base_alarm(
                            self,
                            resource_name=lambda_function["lambda_name"],
                            base_resource=resource,
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
    def lambda_rest_api(self):
        """
        :return: Construct API Gateway.
        """
        return self._lambda_rest_api

    @property
    def authorizer_function(self):
        """
        :return: Construct API Gateway Authorizer Function.
        """
        return self._authorizer_function

    @property
    def lambda_api_router_function(self):
        """
        :return: Construct API Gateway Handler Function.
        """
        return self._lambda_api_router_function

    @property
    def lambda_functions(self):
        """
        :return: Construct API Gateway Handler Function.
        """
        return self._lambda_functions
