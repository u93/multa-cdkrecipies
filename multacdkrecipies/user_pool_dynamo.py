from copy import deepcopy

from aws_cdk import (
    core,
    aws_lambda as lambda_,
    aws_lambda_event_sources as event_sources,
)
from .common import base_alarm, base_cognito_user_pool, base_dynamodb_table, base_lambda_function
from .utils import USER_POOL_DYNAMODB_SCHEMA, validate_configuration


class AwsUserPoolCognitoDynamo(core.Construct):
    """
    AWS CDK Construct that defines a pipe where a message is sent to an SNS Topic and a Lambda function or functions
    subscribed to the topic can process it and take proper actions. The construct allows to set alerts on both resources
    the SNS Topic and the Lambda Functions.
    """

    def __init__(self, scope: core.Construct, id: str, *, prefix: str, environment: str, configuration, **kwargs):
        """
        :param scope: Stack class, used by CDK.
        :param id: ID of the construct, used by CDK.
        :param prefix: Prefix of the construct, used for naming purposes.
        :param environment: Environment of the construct, used for naming purposes.
        :param configuration: Configuration of the construct. In this case SNS_CONFIG_SCHEMA.
        :param kwargs: Other parameters that could be used by the construct.
        """
        super().__init__(scope, id, **kwargs)
        self.prefix = prefix
        self.environment_ = environment
        self._configuration = configuration

        # Validating that the payload passed is correct
        validate_configuration(configuration_schema=USER_POOL_DYNAMODB_SCHEMA, configuration_received=self._configuration)

        # Define Organization DynamoDB Table
        self._organization_table, organization_stream = base_dynamodb_table(self, **self._configuration["organization"])
        self._organization_stream_lambda = None
        if organization_stream is True and self._configuration["organization"]["stream"].get("function") is not None:
            self._organization_stream_lambda = base_lambda_function(
                self, **self._configuration["organization"]["stream"]["function"]
            )

            # Add DynamoDB Stream Trigger to Lambda Function
            self._organization_stream_lambda.add_event_source(
                source=event_sources.DynamoEventSource(
                    table=self._organization_table, starting_position=lambda_.StartingPosition.TRIM_HORIZON, batch_size=1
                )
            )

        # Define User Attributes DynamoDB Table
        self._user_attributes_table, user_attributes_stream = base_dynamodb_table(self, **self._configuration["users_attributes"])
        self._user_attributes_stream_lambda = None
        if user_attributes_stream is True and self._configuration["users_attributes"]["stream"].get("function") is not None:
            self._user_attributes_stream_lambda = base_lambda_function(
                self, **self._configuration["users_attributes"]["stream"]["function"]
            )

            # Add DynamoDB Stream Trigger to Lambda Function
            self._user_attributes_stream_lambda.add_event_source(
                source=event_sources.DynamoEventSource(
                    table=self._user_attributes_table, starting_position=lambda_.StartingPosition.TRIM_HORIZON, batch_size=1,
                )
            )

        # Define Cognito User Pool
        self._user_pool = base_cognito_user_pool(self, **self._configuration["user_pool"])

    def set_alarms(self):
        """
        Function that set alarms for the resources involved in the construct. Except the IoT Rule.
        :return: None
        """
        if self._organization_stream_lambda is None:
            return False
        organization_function = self._configuration["organization"]["stream"]["function"]
        organization_function_alarms = organization_function.get("alarms")
        if isinstance(organization_function_alarms, list) is True:
            organization_streams_alarms = list()
            for alarm_definition in organization_function_alarms:
                organization_streams_alarms.append(
                    base_alarm(
                        self,
                        resource_name=organization_function["lambda_name"],
                        base_resource=self._organization_stream_lambda,
                        **alarm_definition,
                    )
                )

        if self._user_attributes_stream_lambda is None:
            return False
        users_attributes_function = self._configuration["users_attributes"]["stream"]["function"]
        users_attributes_function_alarms = users_attributes_function.get("alarms")
        if isinstance(users_attributes_function_alarms, list) is True:
            users_attributes_streams_alarms = list()
            for alarm_definition in organization_function_alarms:
                users_attributes_streams_alarms.append(
                    base_alarm(
                        self,
                        resource_name=users_attributes_function["lambda_name"],
                        base_resource=self._user_attributes_stream_lambda,
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
    def organization_table(self):
        """
        :return: Construct Organization DynamoDB Table.
        """
        return self._organization_table

    @property
    def organization_stream_lambda(self):
        """
        :return: Construct Organization DynamoDB Streams Lambda.
        """
        return self._organization_stream_lambda

    @property
    def user_attributes_table(self):
        """
        :return: Construct User Attributes DynamoDB Table.
        """
        return self._user_attributes_table

    @property
    def user_attributes_stream_lambda(self):
        """
        :return: Construct User Attributes DynamoDB Streams Lambda.
        """
        return self._user_attributes_stream_lambda

    @property
    def user_pool(self):
        """
        :return: Construct Cognito User Pool.
        """
        return self._user_pool
