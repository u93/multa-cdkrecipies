from aws_cdk import core, aws_cognito as cognito

from .lambda_function import base_lambda_function


def base_cognito_user_pool(construct, **kwargs):
    """
    Function that generates a Cognito User Pool.
    :param construct: Custom construct that will use this function. From the external construct is usually 'self'.
    :param kwargs: Consist of required 'queue_name' and optionals 'queue_delivery_delay' and 'queue_visibility_timeout'.
    :return: DynamoDB Table Construct.
    """
    user_pool_name = construct.prefix + "_" + kwargs["pool_name"] + "_pool_" + construct.environment_

    if kwargs.get("email") is not None:
        email_settings = cognito.EmailSettings(from_=kwargs["email"]["from"], reply_to=kwargs["email"].get("reply_to"))
    else:
        email_settings = None

    password_policy_settings = kwargs.get("password_policy")
    temporary_password_validation_time = (
        core.Duration.days(password_policy_settings.get("temporary_password_duration"))
        if password_policy_settings.get("temporary_password_duration") is not None
        else None
    )
    password_policy = cognito.PasswordPolicy(
        min_length=password_policy_settings.get("minimum_length"),
        temp_password_validity=temporary_password_validation_time,
        require_lowercase=password_policy_settings.get("require", {}).get("lower_case"),
        require_uppercase=password_policy_settings.get("require", {}).get("upper_case"),
        require_digits=password_policy_settings.get("require", {}).get("digits"),
        require_symbols=password_policy_settings.get("require", {}).get("symbols"),
    )

    sign_up_info = kwargs["sign_up"]
    self_sing_up = sign_up_info["enabled"]
    user_verification_info = base_user_verification(sign_up_info=sign_up_info["user_verification"])

    user_invitation = kwargs.get("invitation")
    user_invitation_configuration = cognito.UserInvitationConfig(
        email_subject=user_invitation.get("email", {}).get("subject"),
        email_body=user_invitation.get("email", {}).get("body"),
        sms_message=user_invitation.get("sms", {}).get("body"),
    )

    trigger_functions = kwargs.get("triggers", {})
    lambda_triggers = base_lambda_triggers(construct, trigger_functions=trigger_functions)

    sign_in_list = kwargs.get("sign_in").get("order", list())
    sing_in_kwargs = dict()
    for element in sign_in_list:
        sing_in_kwargs[element] = True
    sign_in_aliases = cognito.SignInAliases(**sing_in_kwargs)

    attributes = kwargs.get("attributes")
    required_attributes_list = attributes.get("standard", list())
    required_attributes_dict = dict()
    for element in required_attributes_list:
        required_attributes_dict[element] = True
    required_attributes = cognito.RequiredAttributes(**required_attributes_dict)

    custom_attributes_list = attributes.get("custom", list())
    custom_attributes = base_custom_attributes(custom_attributes_list=custom_attributes_list)

    user_pool = cognito.UserPool(
        construct,
        id=user_pool_name,
        user_pool_name=user_pool_name,
        email_settings=email_settings,
        password_policy=password_policy,
        self_sign_up_enabled=self_sing_up,
        user_verification=user_verification_info,
        user_invitation=user_invitation_configuration,
        sign_in_aliases=sign_in_aliases,
        required_attributes=required_attributes,
        custom_attributes=custom_attributes,
        lambda_triggers=lambda_triggers,
    )

    if kwargs.get("app_client", {}).get("enabled") is True:
        client_name = kwargs["app_client"]["client_name"]
        generate_secret = kwargs["app_client"]["generate_secret"]
        user_pool_client_name = construct.prefix + "_" + client_name + "_client_" + construct.environment_

        auth_flows = None
        auth_flows_configuration = kwargs["app_client"].get("auth_flows")
        if auth_flows_configuration is not None:
            auth_flows = cognito.AuthFlow(**auth_flows_configuration)

        user_pool.add_client(
            id=user_pool_client_name,
            user_pool_client_name=user_pool_client_name,
            generate_secret=generate_secret,
            auth_flows=auth_flows,
        )

    return user_pool


def base_user_verification(sign_up_info: dict):
    received_email_style = sign_up_info.get("email", {}).get("style")
    if received_email_style == "code":
        email_style = cognito.VerificationEmailStyle.CODE
    elif received_email_style == "link":
        email_style = cognito.VerificationEmailStyle.LINK
    else:
        email_style = None
    user_verification = cognito.UserVerificationConfig(
        email_subject=sign_up_info.get("email", {}).get("subject"),
        email_body=sign_up_info.get("email", {}).get("body"),
        email_style=email_style,
        sms_message=sign_up_info.get("sms", {}).get("body"),
    )

    return user_verification


def base_custom_attributes(custom_attributes_list: list):
    custom_attributes = dict()
    for element in custom_attributes_list:
        if element["type"] == "string":
            custom_attribute = cognito.StringAttribute(
                mutable=element.get("mutable"), min_len=element.get("minimum"), max_len=element.get("maximum")
            )
        elif element["type"] == "number":
            custom_attribute = cognito.NumberAttribute(
                mutable=element.get("mutable"), min=element.get("minimum"), max=element.get("maximum")
            )
        elif element["type"] == "bool":
            custom_attribute = cognito.BooleanAttribute(mutable=element.get("mutable"),)
        elif element["type"] == "date":
            custom_attribute = cognito.DateTimeAttribute(mutable=element.get("mutable"),)
        else:
            continue
        custom_attributes[element] = custom_attribute

    return custom_attributes


def base_lambda_triggers(construct, trigger_functions):
    trigger_functions_data = dict()
    for key in trigger_functions.keys():
        if trigger_functions.get(key) is None:
            continue
        else:
            trigger_functions_data[key] = base_lambda_function(construct, **trigger_functions[key])

    lambda_triggers = cognito.UserPoolTriggers(**trigger_functions_data)
    """
    lambda_triggers = cognito.UserPoolTriggers(
        create_auth_challenge=create_auth_challenge_lambda,
        custom_message=base_lambda_function(construct, **trigger_functions.get("custom_message")),
        define_auth_challenge=base_lambda_function(construct, **trigger_functions.get("define_auth_challenge")),
        post_authentication=base_lambda_function(construct, **trigger_functions.get("post_authentication")),
        post_confirmation=base_lambda_function(construct, **trigger_functions.get("post_confirmation")),
        pre_authentication=base_lambda_function(construct, **trigger_functions.get("pre_authentication")),
        pre_sign_up=base_lambda_function(construct, **trigger_functions.get("pre_sign_up")),
        pre_token_generation=pre_token_generation_,
        user_migration=user_migration_lambda,
        verify_auth_challenge_response=verify_auth_challenge_response_lambda
    )
    """

    return lambda_triggers