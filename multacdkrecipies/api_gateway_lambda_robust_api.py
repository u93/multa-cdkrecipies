import traceback

from aws_cdk import (
    core,
    aws_apigateway as api_gateway,
    aws_cloudwatch as cloudwatch,
    aws_iam as iam,
    aws_lambda as lambda_,
)

from .settings import DEFAULT_LAMBDA_CODE_PATH, DEFAULT_LAMBDA_CODE_PATH_EXISTS
from .utils import APIGATEWAY_LAMBDA_SIMPLE_WEB_SERVICE_SCHEMA, validate_configuration, WrongRuntimePassed


class AwsApiGatewayLambdaPipes(core.Construct):
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
        validate_configuration(
            configuration_schema=APIGATEWAY_LAMBDA_SIMPLE_WEB_SERVICE_SCHEMA, configuration_received=self.configuration
        )
