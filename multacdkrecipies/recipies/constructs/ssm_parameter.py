import json
from aws_cdk import (
    core,
    aws_ssm as ssm,
)
from multacdkrecipies.recipies.utils import SSM_PARAMETER_STRING_SCHEMA, validate_configuration


class AwsSsmString(core.Construct):
    """
    AWS CDK Construct that defines an SSM Parameter Store String to be used by AWS application. Will get a string
    value as a dictionary and then it will convert it as JSON String.
    """

    def __init__(self, scope: core.Construct, id: str, *, prefix: str, environment: str, configuration, **kwargs):
        """
        :param scope: Stack class, used by CDK.
        :param id: ID of the construct, used by CDK.
        :param prefix: Prefix of the construct, used for naming purposes.
        :param environment: Environment of the construct, used for naming purposes.
        :param configuration: Configuration of the construct. In this case SSM_PARAMETER_STRING.
        :param kwargs: Other parameters that could be used by the construct.
        """
        super().__init__(scope, id, **kwargs)
        self.prefix = prefix
        self.environment_ = environment
        self._configuration = configuration

        # Validating that the payload passed is correct
        validate_configuration(configuration_schema=SSM_PARAMETER_STRING_SCHEMA, configuration_received=self._configuration)

        self._parameter_string = ssm.StringParameter(
            self,
            id="/" + self.prefix + "/" + self.environment_ + "/" + self._configuration["name"] + "/appConfig",
            parameter_name="/" + self.prefix + "/" + self.environment_ + "/" + self._configuration["name"] + "/appConfig",
            description=self._configuration.get("description"),
            string_value=json.dumps(self._configuration["string_value"]),
            type=ssm.ParameterType.STRING,
        )

    def grant_read(self, role):
        """
        Grants read permissions to AWS IAM roles.
        :param role: AWS IAM role that will have read access to the AWS SSM String Parameter
        :return:
        """
        self._parameter_string.grant_read(role)

    @property
    def configuration(self):
        """
        :return: Construct configuration.
        """
        return self._configuration

    @property
    def parameter_string(self):
        """
        :return: Construct SSM String Parameter.
        """
        return self._parameter_string
