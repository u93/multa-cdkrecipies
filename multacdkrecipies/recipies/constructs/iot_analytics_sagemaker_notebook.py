import os

from aws_cdk import (
    core,
    aws_iam as iam,
    aws_sagemaker as sagemaker,
)

from multacdkrecipies.recipies.settings import SAGEMAKER_POLICY
from multacdkrecipies.recipies.utils import SAGEMAKER_NOTEBOOK_SCHEMA, validate_configuration, validate_file

file_path = os.path.dirname(os.path.abspath(__file__))


class AwsIoTAnalyticsSageMakerNotebook(core.Construct):
    """
    AWS CDK Construct that defines a Sagemaker Notebook for data analysis as well all the AWS IAM permissions that
    it requires. Also defines the scripts that the Notebook will run On Create and On Start. if the script paths are
    not defined or do not exist they will be taken from the project defined basic scripts.
    """

    def __init__(self, scope: core.Construct, id: str, *, prefix: str, environment: str, configuration, **kwargs):
        """
        :param scope: Stack class, used by CDK.
        :param id: ID of the construct, used by CDK.
        :param prefix: Prefix of the construct, used for naming purposes.
        :param environment: Environment of the construct, used for naming purposes.
        :param configuration: Configuration of the construct. In this case SAGEMAKER_NOTEBOOK.
        :param kwargs: Other parameters that could be used by the construct.
        """
        super().__init__(scope, id, **kwargs)
        self.prefix = prefix
        self.environment_ = environment
        self._configuration = configuration

        # Validating that the payload passed is correct
        validate_configuration(configuration_schema=SAGEMAKER_NOTEBOOK_SCHEMA, configuration_received=configuration)

        base_name = self._configuration["name"]
        on_create_list = list()
        if validate_file(file_path=self._configuration["scripts"]["on_create"]):
            on_create_file = self._configuration["scripts"]["on_create"]
        else:
            on_create_file = file_path + "/scripts/iot_analytics_notebook/on_create.sh"
        with open(on_create_file) as on_create:
            on_create_contents = {"content": core.Fn.base64(on_create.read())}
            on_create_list.append(on_create_contents)

        on_start_list = list()
        if validate_file(file_path=self._configuration["scripts"]["on_create"]):
            on_start_file = self._configuration["scripts"]["on_start"]
        else:
            on_start_file = file_path + "/scripts/iot_analytics_notebook/on_start.sh"
        with open(on_start_file) as on_start:
            on_start_contents = {"content": core.Fn.base64(on_start.read())}
            on_start_list.append(on_start_contents)

        lifecycle_configuration_name = self.prefix + "-" + base_name + "lifecycle-" + self.environment_
        self._lifecycle_configuration = sagemaker.CfnNotebookInstanceLifecycleConfig(
            self,
            id=lifecycle_configuration_name,
            notebook_instance_lifecycle_config_name=lifecycle_configuration_name,
            on_create=on_create_list,
            on_start=on_start_list,
        )

        role_name = self.prefix + "_" + base_name + "sagemaker_role_" + self.environment_
        self._role = iam.Role(
            self, id=role_name, role_name=role_name, assumed_by=iam.ServicePrincipal(service="sagemaker.amazonaws.com")
        )

        managed_policy = iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name="AmazonSageMakerFullAccess")
        self._role.add_managed_policy(policy=managed_policy)

        policy_name = self.prefix + "_" + base_name + "sagemaker_policy" + self.environment_
        ecr_statement = iam.PolicyStatement(actions=SAGEMAKER_POLICY["ecr_actions"], resources=SAGEMAKER_POLICY["ecr_resources"])
        s3_statement = iam.PolicyStatement(actions=SAGEMAKER_POLICY["s3_actions"], resources=SAGEMAKER_POLICY["s3_resources"])
        policy = iam.Policy(self, id=policy_name, policy_name=policy_name, statements=[ecr_statement, s3_statement])
        self._role.attach_inline_policy(policy=policy)

        sagemaker_notebook_name = self.prefix + "_" + base_name + "sagemaker_notebook_" + self.environment_
        self._sagemaker_notebook = sagemaker.CfnNotebookInstance(
            self,
            id=sagemaker_notebook_name,
            notebook_instance_name=sagemaker_notebook_name,
            lifecycle_config_name=self._lifecycle_configuration.notebook_instance_lifecycle_config_name,
            role_arn=self._role.role_arn,
            instance_type=self._configuration["instance_type"],
        )

    @property
    def configuration(self):
        """
        :return: Construct configuration.
        """
        return self._configuration

    @property
    def lifecycle_configuration(self):
        """
        :return: Construct lifecycle configuration.
        """
        return self._lifecycle_configuration

    @property
    def role(self):
        """
        :return: Construct IAM Role.
        """
        return self._role

    @property
    def sagemaker_notebook(self):
        """
        :return: Construct Sagemaker Notebook.
        """
        return self._sagemaker_notebook
