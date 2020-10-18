from aws_cdk import (
    core,
)
from multacdkrecipies.common import base_bucket
from multacdkrecipies.recipies.utils import S3_BUCKETS_CLUSTER_SCHEMA, validate_configuration


class AwsS3BucketsCluster(core.Construct):
    """"""

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
        validate_configuration(configuration_schema=S3_BUCKETS_CLUSTER_SCHEMA, configuration_received=self._configuration)

        # Define S3 Buckets Cluster
        self._s3_buckets = list()
        for bucket in self._configuration["buckets"]:
            _bucket = base_bucket(self, **bucket)
            self._s3_buckets.append(_bucket)

    @property
    def s3_buckets(self):
        """
        :return: Construct S3 Buckets List.
        """
        return self._s3_buckets
