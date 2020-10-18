from aws_cdk import (
    core,
    aws_apigateway as api_gateway,
    aws_certificatemanager as cert_manager,
    aws_lambda as lambda_,
)
from multacdkrecipies.common import base_bucket, base_alarm, base_lambda_function
from multacdkrecipies.recipies.utils import APIGATEWAY_SIMPLE_WEB_SERVICE_SCHEMA, validate_configuration


class AwsApiGatewayLambdaSWS(core.Construct):
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
            configuration_schema=APIGATEWAY_SIMPLE_WEB_SERVICE_SCHEMA, configuration_received=self._configuration
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
        custom_domain = api_configuration["root_resource"].get("custom_domain")
        if custom_domain is not None:
            domain_name = custom_domain["domain_name"]
            certificate_arn = custom_domain["certificate_arn"]
            domain_options = api_gateway.DomainNameOptions(
                certificate=cert_manager.Certificate.from_certificate_arn(self, id=domain_name, certificate_arn=certificate_arn),
                domain_name=domain_name,
            )

        # Define API Gateway Lambda Handler
        self._handler_function = base_lambda_function(self, **api_configuration["root_resource"]["handler"])

        if api_configuration["proxy"] is False and api_configuration.get("root_resource").get("methods") is None:
            print("Unable to check which method to use for the API! Use proxy: True or define methods...")
            raise RuntimeError

        self._lambda_rest_api = api_gateway.LambdaRestApi(
            self,
            id=api_configuration["apigateway_name"],
            rest_api_name=api_configuration["apigateway_name"],
            description=api_configuration["apigateway_description"],
            domain_name=domain_options,
            handler=self._handler_function,
            proxy=api_configuration["proxy"],
            cloud_watch_role=True,
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

        # Define Gateway Resource and Methods
        resource = self._lambda_rest_api.root.add_resource(api_configuration["root_resource"]["name"])
        allowed_origins = api_configuration["root_resource"].get("allowed_origins")
        if api_configuration["proxy"] is False:
            gateway_methods = api_configuration["root_resource"]["methods"]
            for method in gateway_methods:
                resource.add_method(http_method=method, authorizer=gateway_authorizer)

            if allowed_origins is not None:
                resource.add_cors_preflight(allow_origins=allowed_origins, allow_methods=gateway_methods)
        else:
            if allowed_origins is not None:
                resource.add_cors_preflight(allow_origins=allowed_origins)

    def set_alarms(self):
        """
        Function that set alarms for the resources involved in the construct. Except API Gateway resource.
        :return: None
        """
        if isinstance(self._configuration["api"]["root_resource"]["handler"].get("alarms"), list) is True:
            authorizer_alarms = list()
            for alarm_definition in self._configuration["api"]["root_resource"]["handler"].get("alarms"):
                authorizer_alarms.append(
                    base_alarm(
                        self,
                        resource_name="lambda_api_handler",
                        base_resource=self._handler_lambda_functions,
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
    def handler_function(self):
        """
        :return: Construct API Gateway Handler Function.
        """
        return self._handler_function
