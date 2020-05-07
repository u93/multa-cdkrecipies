from aws_cdk import aws_cognito as cognito


def base_cognito_user_groups(construct, **kwargs):
    """
    Function that generates a Cognito User Pool Groups.
    :param construct: Custom construct that will use this function. From the external construct is usually 'self'.
    :param kwargs: Consist of required 'queue_name' and optionals 'queue_delivery_delay' and 'queue_visibility_timeout'.
    :return: DynamoDB Table Construct.
    """
    user_pool_group_name = construct.prefix + "_" + kwargs["group_name"] + "_group_" + construct.environment_
    user_pool_group_description = kwargs.get("description")
    user_pool_group_id = kwargs["pool_id"]
    user_pool_group_precendence = kwargs["precedence"]
    user_pool_group_role_arn = kwargs["role_arn"]

    user_pool_group = cognito.CfnUserPoolGroup(
        construct,
        id=user_pool_group_name,
        group_name=user_pool_group_name,
        description=user_pool_group_description,
        user_pool_id=user_pool_group_id,
        precedence=user_pool_group_precendence,
        role_arn=user_pool_group_role_arn,
    )

    return user_pool_group
