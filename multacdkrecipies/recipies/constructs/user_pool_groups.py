from aws_cdk import core
from multacdkrecipies.common import base_cognito_user_groups, base_service_role
from multacdkrecipies.recipies.utils import USER_POOL_GROUPS_SCHEMA, validate_configuration


class AwsUserPoolCognitoGroups(core.Construct):
    """
    AWS CDK Construct that defines a Cognito User Pool Groups and their specific Roles attached. The reason behind this
    Construct is trying to simplify the creation of this due the lack of high-order resources_constructs.
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
        validate_configuration(configuration_schema=USER_POOL_GROUPS_SCHEMA, configuration_received=self._configuration)

        self._groups_roles_list = list()
        for group_definition in self._configuration["user_pool_groups"]:
            role = base_service_role(
                self,
                resource_name=group_definition["role"]["name"],
                actions=group_definition["role"]["actions"],
                resources=group_definition["role"]["resources"],
                principal_resource=group_definition["role"]["principal"],
            )

            kwargs["role_arn"] = role.role_arn
            user_group = base_cognito_user_groups(self, **kwargs)

            self._groups_roles_list.append({"user_group": user_group, "role": role})

    @property
    def configuration(self):
        """
        :return: Construct configuration.
        """
        return self._configuration

    @property
    def groups_roles_list(self):
        """
        :return: List of resources_constructs containing dictionaries with Group Resource and Role Resource.
        """
        return self._groups_roles_list
