import os
import subprocess

from aws_cdk import core
from multacdkrecipies.common import base_lambda_layer
from multacdkrecipies.recipies.settings.lambda_layer_settings import (
    DEFAULT_LAMBDA_LAYER_CODE_PATH,
    DEFAULT_LAMBDA_LAYER_CODE_PATH_EXISTS,
    DEFAULT_LAMBDA_LAYER_REQUIREMENTS_PATH,
    DEFAULT_LAMBDA_LAYER_REQUIREMENTS_PATH_EXISTS,
    DEFAULT_LAMBDA_LAYER_CODE_INSTALL_PATH,
)
from multacdkrecipies.recipies.utils import LAMBDA_LAYER_SCHEMA, validate_configuration


class AwsLambdaLayerVenv(core.Construct):
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

        layer_paths = self._configuration.get("paths")
        if layer_paths is not None:
            layer_code_path = layer_paths["layer_code_path"]
            layer_directory_path = layer_paths["layer_directory_path"]
            requirements_path = layer_paths["python_requirements_file_path"]
        else:
            if DEFAULT_LAMBDA_LAYER_CODE_PATH_EXISTS is True:
                layer_code_path = DEFAULT_LAMBDA_LAYER_CODE_PATH
                layer_directory_path = DEFAULT_LAMBDA_LAYER_CODE_INSTALL_PATH
            else:
                print(f"Code path for Lambda Layer {self._configuration['layer_name']} is not valid!")
                raise RuntimeError

            if DEFAULT_LAMBDA_LAYER_REQUIREMENTS_PATH_EXISTS is True:
                requirements_path = DEFAULT_LAMBDA_LAYER_REQUIREMENTS_PATH
            else:
                print(f"Lambda Python requirements path for Lambda Layer {self._configuration['layer_name']} is not valid!")
                raise RuntimeError

        subprocess_command = [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{os.environ.get('PWD')}:/foo",
            "-w",
            "/foo",
            "lambci/lambda:build-python3.7",
            "pip",
            "install",
            "-r",
            requirements_path,
            "-t",
            layer_directory_path,
        ]
        if self._configuration.get("dependencies", False) is False:
            subprocess_command.append("--no-dependencies")
        subprocess.call(subprocess_command)

        self._configuration["layer_code_path"] = layer_code_path
        self._lambda_layer = base_lambda_layer(self, **self._configuration)

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
