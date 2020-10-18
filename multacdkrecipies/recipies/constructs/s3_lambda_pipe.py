from copy import deepcopy
from aws_cdk import (
    core,
    aws_lambda_event_sources as events,
    aws_s3 as s3,
)
from multacdkrecipies.common import base_alarm, base_lambda_function, base_bucket
from multacdkrecipies.recipies.utils import S3_LAMBDA_CONFIG_SCHEMA, validate_configuration, enum_parsing


class AwsS3LambdaPipes(core.Construct):
    """"""

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
        validate_configuration(configuration_schema=S3_LAMBDA_CONFIG_SCHEMA, configuration_received=self._configuration)

        # Defining S3 Bucket
        bucket_data = deepcopy(self._configuration["bucket"])
        self._s3_bucket = base_bucket(self, **bucket_data)

        # Validating Lambda Function Runtime
        functions_data = self._configuration["lambda_handler"]
        self._lambda_function = base_lambda_function(self, **functions_data)

        # Defining the Lambda subscription to the specified S3 Bucket in cdk.json file.
        s3_events = self._configuration["events"]
        event_list = enum_parsing(source_list=s3_events,target_enum=s3.EventType)

        s3_subscription = events.S3EventSource(bucket=self._s3_bucket, events=event_list)
        self._lambda_function.add_event_source(source=s3_subscription)

    def set_alarms(self):
        """
        Function that set alarms for the resources involved in the construct.
        :return: None
        """
        pass

    @property
    def configuration(self):
        """
        :return: Construct configuration.
        """
        return self._configuration

    @property
    def lambda_function(self):
        """
        :return: Construct configuration.
        """
        return self._lambda_function

    @property
    def s3_bucket(self):
        """
        :return: Construct configuration.
        """
        return self._s3_bucket
