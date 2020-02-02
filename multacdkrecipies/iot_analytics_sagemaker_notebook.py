import os

from aws_cdk import (
    core,
    aws_iam as iam,
    aws_sagemaker as sagemaker,
)

from .settings import SAGEMAKER_POLICY
from .utils import SAGEMAKER_NOTEBOOK, validate_configuration, validate_file, WrongTypeException

file_path = os.path.dirname(os.path.abspath(__file__))


class AwsIoTAnalyticsSageMakerNotebook(core.Construct):
    """
    AWS CDK Construct that defines a pipe where a Rules captures an MQTT Message sent to or from AWS IoT MQTT Broker,
    then the message is sent to an SQS Queue and a Lambda function subscribed to the topic can process it and take
    proper actions. The construct takes a few inputs.

    Attributes:
        prefix (str): The prefix set on the name of each resource created in the stack. Just for organization purposes.
        environment_ (str): The environment that all resources will use. Also for organizational and testing purposes.

    """

    def __init__(self, scope: core.Construct, id: str, *, prefix: str, environment: str, configuration, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.prefix = prefix
        self.environment_ = environment
        validate_configuration(configuration_schema=SAGEMAKER_NOTEBOOK, configuration_received=configuration)

        base_name = configuration["name"]

        on_create_list = list()
        if validate_file(file_path=configuration["scripts"]["on_create"]):
            on_create_file = configuration["scripts"]["on_create"]
        else:
            os.path.dirname(os.path.abspath(__file__))
            on_create_file = file_path + "/scripts/iot_analytics_notebook/on_create.sh"
        with open(on_create_file) as on_create:
            on_create_contents = {"content": core.Fn.base64(on_create.read())}
            on_create_list.append(on_create_contents)

        on_start_list = list()
        if validate_file(file_path=configuration["scripts"]["on_create"]):
            on_start_file = configuration["scripts"]["on_start"]
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
        ecr_statement = iam.PolicyStatement(
            actions=SAGEMAKER_POLICY["ecr_actions"], resources=SAGEMAKER_POLICY["ecr_resources"]
        )
        s3_statement = iam.PolicyStatement(
            actions=SAGEMAKER_POLICY["s3_actions"], resources=SAGEMAKER_POLICY["s3_resources"]
        )
        policy = iam.Policy(self, id=policy_name, policy_name=policy_name, statements=[ecr_statement, s3_statement])
        self._role.attach_inline_policy(policy=policy)

        sagemaker_notebook_name = self.prefix + "_" + base_name + "sagemaker_notebook_" + self.environment_
        self._sagemaker_notebook = sagemaker.CfnNotebookInstance(
            self,
            id=sagemaker_notebook_name,
            notebook_instance_name=sagemaker_notebook_name,
            lifecycle_config_name=self._lifecycle_configuration.notebook_instance_lifecycle_config_name,
            role_arn=self._role.role_arn,
            instance_type=configuration["instance_type"],
        )

    @property
    def lifecycle_configuration(self):
        return self._lifecycle_configuration

    @property
    def role(self):
        return self._role

    @property
    def sagemaker_notebook(self):
        return self._sagemaker_notebook
