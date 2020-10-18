from aws_cdk import (
    core,
    aws_lambda as lambda_,
    aws_lambda_event_sources as event_sources,
)
from multacdkrecipies.common import (
    base_bucket,
    base_cognito_user_pool,
    base_cognito_user_identity_pool,
    base_dynamodb_table,
    base_lambda_function,
)

from multacdkrecipies.recipies.utils import USER_SERVERLESS_BACKEND_SCHEMA, validate_configuration


class AwsUserServerlessBackend(core.Construct):
    """
    AWS CDK Construct that defines a Backend for User Management including a Cognito User Pool with the respective
    Lambda Triggers and also the possibility to configure DynamoDB tables to match necessities that may arise that
    the Cognito User Pool can't match.
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
        validate_configuration(configuration_schema=USER_SERVERLESS_BACKEND_SCHEMA, configuration_received=self._configuration)

        # Define Lambda Authorizer Function
        authorizer_functions = self._configuration.get("authorizer_function")
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

        # Define DynamoDB Tables
        self._dynamodb_tables_lambda_functions = list()
        for table in self._configuration.get("dynamo_tables", []):
            table, stream = base_dynamodb_table(self, **table)
            stream_lambda = None
            if stream is True and table["stream"].get("function") is not None:
                stream_lambda = base_lambda_function(self, **table["stream"]["function"])

                # Add DynamoDB Stream Trigger to Lambda Function
                stream_lambda.add_event_source(
                    source=event_sources.DynamoEventSource(
                        table=table, starting_position=lambda_.StartingPosition.TRIM_HORIZON, batch_size=1
                    )
                )

            self._dynamodb_tables_lambda_functions.append({"table": table, "stream_lambda": stream_lambda})

        # Define S3 Buckets Cluster
        if isinstance(self._configuration.get("buckets"), list):
            self._s3_buckets = [base_bucket(self, **bucket) for bucket in self._configuration["buckets"]]

        # Define Cognito User Pool
        user_pool_config = self._configuration["user_pool"]
        self._user_pool, self._user_pool_client = base_cognito_user_pool(self, **user_pool_config)

        if user_pool_config.get("identity_pool") is not None and self._user_pool_client is not None:
            self._identity_pool = base_cognito_user_identity_pool(
                self,
                user_pool_client_id=self._user_pool_client.user_pool_client_id,
                user_pool_provider_name=self._user_pool.user_pool_provider_name,
                **user_pool_config["identity_pool"],
            )

    @property
    def configuration(self):
        """
        :return: Construct configuration.
        """
        return self._configuration

    @property
    def authorizer_function(self):
        """
        :return: Construct Authorizer Lambda Function.
        """
        return self._authorizer_function

    @property
    def dynamodb_tables_lambda_functions(self):
        """
        :return: List of dictionaries containing construct DynamoDB Tables and Stream Lambda functions.
        """
        return self._dynamodb_tables_lambda_functions

    @property
    def user_pool(self):
        """
        :return: Construct Cognito User Pool.
        """
        return self._user_pool

    @property
    def identity_pool(self):
        """
        :return: Construct Cognito Identity Pool.
        """
        return self._identity_pool
