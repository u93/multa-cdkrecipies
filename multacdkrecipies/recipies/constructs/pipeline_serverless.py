from aws_cdk import core
from multacdkrecipies.recipies.utils import SNS_CONFIG_SCHEMA, validate_configuration


class PipelineServerless(core.Construct):
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
        validate_configuration(configuration_schema=SNS_CONFIG_SCHEMA, configuration_received=self._configuration)
