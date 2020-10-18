from aws_cdk import (
    core,
    aws_iot as iot_,
)

from multacdkrecipies.recipies.utils import IOT_POLICY_SCHEMA, validate_configuration


class AwsIotPolicy(core.Construct):
    """
    AWS CDK Construct that defines an AWS Analytics Pipeline with simple Data Flow approach where one channel
    ingests all the information and distributes over a Pipeline that is attached to a common Datastore.
    """

    def __init__(self, scope: core.Construct, id: str, *, prefix: str, environment: str, configuration, **kwargs):
        """
        :param scope: Stack class, used by CDK.
        :param id: ID of the construct, used by CDK.
        :param prefix: Prefix of the construct, used for naming purposes.
        :param environment: Environment of the construct, used for naming purposes.
        :param configuration: Configuration of the construct. In this case IOT_ANALYTICS_DATA_WORKFLOW.
        :param kwargs: Other parameters that could be used by the construct.
        """
        super().__init__(scope, id, **kwargs)
        self.prefix = prefix
        self.environment_ = environment
        self._configuration = configuration

        # Validating that the payload passed is correct
        validate_configuration(configuration_schema=IOT_POLICY_SCHEMA, configuration_received=self._configuration)

        self._iot_policy = iot_.CfnPolicy(
            self,
            id=self.prefix + "_" + self._configuration["name"] + "_" + self.environment_,
            policy_name=self.prefix + "_" + self._configuration["name"] + "_" + self.environment_,
            policy_document=self._configuration["policy_document"],
        )

    @property
    def configuration(self):
        """
        :return: Construct configuration.
        """
        return self._configuration

    @property
    def iot_policy(self):
        """
        :return: Construct IoT Policy.
        """
        return self._iot_policy
