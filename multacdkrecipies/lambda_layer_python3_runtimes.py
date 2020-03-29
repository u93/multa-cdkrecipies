from copy import deepcopy

from aws_cdk import (
    core,
    aws_sns_subscriptions as sns_subs,
)
from .common import base_lambda_layer
from .utils import LAMBDA_LAYER_SCHEMA, validate_configuration


class AwsLambdaLayer(core.Construct):
    """
    AWS CDK Construct that defines a Lambda Layer that gets .
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
        validate_configuration(configuration_schema=LAMBDA_LAYER_SCHEMA, configuration_received=self._configuration)
        _lambda_layer = base_lambda_layer(self, **self._configuration)

    @property
    def configuration(self):
        """
        :return: Construct configuration.
        """
        return self._configuration

    @property
    def lambda_layer(self):
        """
        :return: Construct Lambda Layer.
        """
        return self._lambda_layer
