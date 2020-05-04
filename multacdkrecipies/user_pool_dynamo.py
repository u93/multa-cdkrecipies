from aws_cdk import (
    core,
    aws_lambda as lambda_,
    aws_lambda_event_sources as event_sources,
)
from .common import base_cognito_user_pool, base_dynamodb_table, base_lambda_function
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
        self._dynamodb_tables = list()
        for table in self._configuration["organization"]["dynamo_tables"]:
            table, stream = base_dynamodb_table(self, **table)
            stream_lambda = None
            if stream is True and table["stream"].get("function") is not None:
                stream_lambda = base_lambda_function(
                    self, **table["stream"]["function"]
                )

                # Add DynamoDB Stream Trigger to Lambda Function
                stream_lambda.add_event_source(
                    source=event_sources.DynamoEventSource(
                        table=table, starting_position=lambda_.StartingPosition.TRIM_HORIZON, batch_size=1
                    )
                )

            self._dynamodb_tables.append({"table": table, "stream_lambda": stream_lambda})

        # Define Cognito User Pool
        self._user_pool = base_cognito_user_pool(self, **self._configuration["user_pool"])

    @property
    def configuration(self):
        """
        :return: Construct configuration.
        """
        return self._configuration

    @property
    def dynamodb_tables(self):
        """
        :return: Construct DynamoDB Tables and Stream Lambda functions.
        """
        return self._dynamodb_tables

    @property
    def user_pool(self):
        """
        :return: Construct Cognito User Pool.
        """
        return self._user_pool
