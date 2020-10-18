from aws_cdk import (
    core,
)
from multacdkrecipies.common import base_alarm, base_lambda_function, base_topic
from multacdkrecipies.recipies.utils import SNS_CONFIG_SCHEMA, validate_configuration


class AwsSnsPipes(core.Construct):
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
        validate_configuration(configuration_schema=SNS_CONFIG_SCHEMA, configuration_received=self._configuration)

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
