from aws_cdk import core, aws_cognito as cognito

from .role import base_cognito_identity_pool_auth_role, base_cognito_identity_pool_unauth_role


def base_cognito_user_identity_pool(construct, user_pool_client_id, user_pool_provider_name, **kwargs):
    """
    Function that generates a Cognito Identity Pool.
    :param construct: Custom construct that will use this function. From the external construct is usually 'self'.
    :param user_pool_client_id: Client ID of a Cognito User Pool.
    :param user_pool_provider_name: Provider Name of a Cognito User Pool.
    :param kwargs: Consist of required 'pool_name' and others.
    :return: Cognito Identity Pool Construct.
    """
    indentity_pool_name = construct.prefix + "_" + kwargs["identity_pool_name"] + "_idpool_" + construct.environment_

    allow_unauth_identities = kwargs.get("allow_unauth_identities", False)
    cognito_identity_provider = cognito.CfnIdentityPool.CognitoIdentityProviderProperty(
        client_id=user_pool_client_id, provider_name=user_pool_provider_name
    )

    identity_pool = cognito.CfnIdentityPool(
        construct,
        id=indentity_pool_name,
        identity_pool_name=indentity_pool_name,
        allow_unauthenticated_identities=allow_unauth_identities,
        cognito_identity_providers=[cognito_identity_provider],
    )

    base_cognito_user_identity_pool_attach_role(
        construct,
        identity_pool=identity_pool,
        unauth_role_config=kwargs["unauth_role"],
        auth_role_config=kwargs["auth_role"],
    )

    return identity_pool


def base_cognito_user_identity_pool_attach_role(construct, identity_pool, unauth_role_config, auth_role_config):
    """
    Function that attach Roles to an Identity Pool.
    :param construct: Custom construct that will use this function. From the external construct is usually 'self'.
    :param identity_pool:
    :param unauth_role_config:
    :param auth_role_config:
    :return:
    """
    base_role_name = identity_pool.identity_pool_name
    unauth_actions = unauth_role_config["actions"]
    unauth_resources = unauth_role_config["resources"]
    auth_actions = auth_role_config["actions"]
    auth_resources = auth_role_config["resources"]

    unauth_role = base_cognito_identity_pool_unauth_role(
        construct, identity_pool, resource_name=base_role_name, actions=unauth_actions, resources=unauth_resources
    )
    auth_role = base_cognito_identity_pool_auth_role(
        construct, identity_pool, resource_name=base_role_name, actions=auth_actions, resources=auth_resources
    )

    role_attachment = cognito.CfnIdentityPoolRoleAttachment(
        construct,
        id=identity_pool.identity_pool_name + "_roleattach",
        identity_pool_id=identity_pool.ref,
        roles={"unauthenticated": unauth_role.role_arn, "authenticated": auth_role.role_arn},
    )

    return role_attachment
