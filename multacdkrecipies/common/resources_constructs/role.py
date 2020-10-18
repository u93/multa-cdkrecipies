import traceback

from aws_cdk import aws_iam as iam, core


def base_service_role(construct, resource_name: str, principal_resource: str, actions: list, resources: list):
    """
    Function that generates an IAM Service Role with a Policy.
    :param construct: Custom construct that will use this function. From the external construct is usually 'self'.
    :param resource_name: Name of the resource. Used for naming purposes.
    :param principal_resource: Resource used to define a Service Principal. Has to match an AWS Resource. For example, 'iot' -> 'iot.amazonaws.com'.
    :param actions: Action list containing AWS IAM defined actions. For example 'sns:Publish'
    :param resources: List of resources ARNs defined by AWS.
    :return: IAM Service Role with an IAM Policy attached.
    """
    try:
        # Defining IAM Role
        # Defining Service Principal
        iam_role_name = construct.prefix + "_role_" + resource_name + "_" + construct.environment_
        iam_policy_name = construct.prefix + "_policy_" + resource_name + "_" + construct.environment_
        principal = iam.ServicePrincipal(service=f"{principal_resource}.amazonaws.com")

        # Defining IAM Role
        role = iam.Role(construct, id=iam_role_name, role_name=iam_role_name, assumed_by=principal)

        # Defining Policy Statement, Policy and Attaching to Role
        policy_statements = iam.PolicyStatement(actions=actions, resources=resources)
        policy = iam.Policy(construct, id=iam_policy_name, policy_name=iam_policy_name, statements=[policy_statements])
        policy.attach_to_role(role=role)

    except Exception:
        print(traceback.format_exc())
    else:
        return role


def base_federated_role(
    construct,
    resource_name: str,
    federated_resource: str,
    assume_role_action: str,
    conditions: dict,
    actions: list,
    resources: list,
):
    """
    Function that generates an IAM Federated Role with a Policy.
    :param construct: Custom construct that will use this function. From the external construct is usually 'self'.
    :param resource_name: Name of the resource. Used for naming purposes.
    :param federated_resource: Resource used to define a Federated Principal. Has to match an AWS Resource. For example, 'cognito-identity' -> 'cognito-identity.amazonaws.com'.
    :param assume_role_action: The conditions under which the policy is in effect.
    :param conditions: Generally an STS Action.
    :param actions: Action list containing AWS IAM defined actions. For example 'sns:Publish'
    :param resources: List of resources ARNs defined by AWS.
    :return: IAM Federated Role with an IAM Policy attached.
    """
    try:
        # Defining IAM Role
        # Defining Service Principal
        iam_role_name = construct.prefix + "_role_" + resource_name + "_" + construct.environment_
        iam_policy_name = construct.prefix + "_policy_" + resource_name + "_" + construct.environment_
        principal = iam.FederatedPrincipal(
            federated=f"{federated_resource}.amazonaws.com",
            conditions=conditions,
            assume_role_action=assume_role_action,
        )

        # Defining IAM Role
        role = iam.Role(construct, id=iam_role_name, role_name=iam_role_name, assumed_by=principal)

        # Defining Policy Statement, Policy and Attaching to Role
        policy_statements = iam.PolicyStatement(actions=actions, resources=resources)
        policy = iam.Policy(construct, id=iam_policy_name, policy_name=iam_policy_name, statements=[policy_statements])
        policy.attach_to_role(role=role)

    except Exception:
        print(traceback.format_exc())
    else:
        return role


def base_lambda_role(construct, resource_name: str, principal_resource: str, resources: list, **kwargs):
    """
    Function that generates an IAM Role with a Policy for Lambda Invoke.
    :param construct: Custom construct that will use this function. From the external construct is usually 'self'.
    :param resource_name: Name of the ROLE resource. Used for naming purposes.
    :param principal_resource: Resource used to define a Service Principal. Has to match an AWS Resource. For example, 'iot' -> 'iot.amazonaws.com'.
    :param kwargs: Other parameters that could be used by the construct.
    :return: IAM Role with an IAM Policy attached.
    """
    try:
        actions = ["lambda:InvokeFunction"]
        resources = [function.topic_arn for function in resources]
        role = base_service_role(construct, resource_name, principal_resource, actions=actions, resources=resources)
    except Exception:
        print(traceback.format_exc())
    else:
        return role


def base_sns_role(construct, resource_name: str, principal_resource: str, **kwargs):
    """
    Function that generates an IAM Role with a Policy for SNS Publishing.
    :param construct: Custom construct that will use this function. From the external construct is usually 'self'.
    :param resource_name: Name of the resource. Used for naming purposes.
    :param principal_resource: Resource used to define a Service Principal. Has to match an AWS Resource. For example, 'iot' -> 'iot.amazonaws.com'.
    :param kwargs: Other parameters that could be used by the construct.
    :return: IAM Role with an IAM Policy attached.
    """
    try:
        actions = ["sns:Publish"]
        resources = [construct._sns_topic.topic_arn]
        role = base_service_role(construct, resource_name, principal_resource, actions=actions, resources=resources)
    except Exception:
        print(traceback.format_exc())
    else:
        return role


def base_sqs_role(construct, resource_name: str, principal_resource: str, **kwargs):
    """
    Function that generates an IAM Role with a Policy for SQS Send Message.
    :param construct: Custom construct that will use this function. From the external construct is usually 'self'.
    :param resource_name: Name of the resource. Used for naming purposes.
    :param principal_resource: Resource used to define a Service Principal. Has to match an AWS Resource. For example, 'iot' -> 'iot.amazonaws.com'.
    :param kwargs: Other parameters that could be used by the construct.
    :return: IAM Role with an IAM Policy attached.
    """
    try:
        actions = ["sqs:SendMessage"]
        resources = [construct._sqs_queue.queue_arn]
        role = base_service_role(construct, resource_name, principal_resource, actions=actions, resources=resources)
    except Exception:
        print(traceback.format_exc())
    else:
        return role


def base_kinesis_role(construct, resource_name: str, principal_resource: str, **kwargs):
    """
    Function that generates an IAM Role with a Policy for SQS Send Message.
    :param construct: Custom construct that will use this function. From the external construct is usually 'self'.
    :param resource_name: Name of the resource. Used for naming purposes.
    :param principal_resource: Resource used to define a Service Principal. Has to match an AWS Resource. For example, 'iot' -> 'iot.amazonaws.com'.
    :param kwargs: Other parameters that could be used by the construct.
    :return: IAM Role with an IAM Policy attached.
    """
    try:
        actions = ["kinesis:PutRecord"]
        resources = [construct._kinesis_stream.stream_arn]
        role = base_service_role(construct, resource_name, principal_resource, actions=actions, resources=resources)
    except Exception:
        print(traceback.format_exc())
    else:
        return role


def base_kinesis_firehose_role(construct, resource_name: str, principal_resource: str, **kwargs):
    """
    Function that generates an IAM Role with a Policy for Kinesis Delivery Stream Put Record.
    :param construct: Custom construct that will use this function. From the external construct is usually 'self'.
    :param resource_name: Name of the resource. Used for naming purposes.
    :param principal_resource: Resource used to define a Service Principal. Has to match an AWS Resource. For example, 'iot' -> 'iot.amazonaws.com'.
    :param kwargs: Other parameters that could be used by the construct.
    :return: IAM Role with an IAM Policy attached.
    """
    try:
        actions = ["firehose:PutRecord"]
        resources = [construct._kinesis_firehose_stream.attr_arn]
        role = base_service_role(construct, resource_name, principal_resource, actions=actions, resources=resources)
    except Exception:
        print(traceback.format_exc())
    else:
        return role


def base_kinesis_firehose_s3_role(construct, resource_name: str, principal_resource: str, **kwargs):
    """
    Function that generates an IAM Role with a Policy for Kinesis Stream Put Record.
    :param construct: Custom construct that will use this function. From the external construct is usually 'self'.
    :param resource_name: Name of the resource. Used for naming purposes.
    :param principal_resource: Resource used to define a Service Principal. Has to match an AWS Resource. For example, 'iot' -> 'iot.amazonaws.com'.
    :param kwargs: Other parameters that could be used by the construct.
    :return: IAM Role with an IAM Policy attached.
    """
    try:
        actions = ["firehose:PutRecord"]
        resources = [construct._kinesis_firehose_stream.attr_arn]
        role = base_service_role(construct, resource_name, principal_resource, actions=actions, resources=resources)
    except Exception:
        print(traceback.format_exc())
    else:
        return role


def base_iot_analytics_role(construct, resource_name: str, principal_resource: str, **kwargs):
    """
    Function that generates an IAM Role with a Policy for IoT Analytics Batch Put Message.
    :param construct: Custom construct that will use this function. From the external construct is usually 'self'.
    :param resource_name: Name of the resource. Used for naming purposes.
    :param principal_resource: Resource used to define a Service Principal. Has to match an AWS Resource. For example, 'iot' -> 'iot.amazonaws.com'.
    :param kwargs: Other parameters that could be used by the construct.
    :return: IAM Role with an IAM Policy attached.
    """
    try:
        actions = ["iotanalytics:BatchPutMessage"]
        stack_object = core.Stack.of(construct)
        resource_arn = stack_object.format_arn(service="iotanalytics", resource="channel", resource_name=resource_name)

        resources = [resource_arn]
        role = base_service_role(construct, resource_name, principal_resource, actions=actions, resources=resources)
    except Exception:
        print(traceback.format_exc())
    else:
        return role


def base_cognito_identity_pool_unauth_role(
    construct, identity_pool, resource_name: str, actions: list, resources: list, **kwargs
):
    """
    Function that generates an IAM Role with a Policy for IoT Analytics Batch Put Message.
    :param construct: Custom construct that will use this function. From the external construct is usually 'self'.
    :param resource_name: Name of the resource. Used for naming purposes.
    :param identity_pool:
    :param actions: IAM Actions allowed for Unauthenticated Users.
    :param resources: IAM Resources allowed for Unauthenticated Users.
    :param kwargs: Other parameters that could be used by the construct.
    :return: IAM Role with an IAM Policy attached.
    """
    try:
        federated_resource = "cognito-identity"
        conditions = {
            "StringEquals": {"cognito-identity.amazonaws.com:aud": identity_pool.ref},
            "ForAnyValue:StringLike": {"cognito-identity.amazonaws.com:amr": "unauthenticated"},
        }
        assume_role_action = "sts:AssumeRoleWithWebIdentity"
        role = base_federated_role(
            construct,
            resource_name + "_unauthrole",
            federated_resource,
            conditions=conditions,
            assume_role_action=assume_role_action,
            actions=actions,
            resources=resources,
        )
    except Exception:
        print(traceback.format_exc())
    else:
        return role


def base_cognito_identity_pool_auth_role(construct, identity_pool, resource_name: str, actions: list, resources: list, **kwargs):
    """
    Function that generates an IAM Role with a Policy for IoT Analytics Batch Put Message.
    :param construct: Custom construct that will use this function. From the external construct is usually 'self'.
    :param identity_pool:
    :param resource_name: Name of the resource. Used for naming purposes.
    :param actions: IAM Actions allowed for Unauthenticated Users.
    :param resources: IAM Resources allowed for Unauthenticated Users.
    :param kwargs: Other parameters that could be used by the construct.
    :return: IAM Role with an IAM Policy attached.
    """
    try:
        federated_resource = "cognito-identity"
        conditions = {
            "StringEquals": {"cognito-identity.amazonaws.com:aud": identity_pool.ref},
            "ForAnyValue:StringLike": {"cognito-identity.amazonaws.com:amr": "authenticated"},
        }
        assume_role_action = "sts:AssumeRoleWithWebIdentity"
        role = base_federated_role(
            construct,
            resource_name + "_authrole",
            federated_resource,
            conditions=conditions,
            assume_role_action=assume_role_action,
            actions=actions,
            resources=resources,
        )
    except Exception:
        print(traceback.format_exc())
    else:
        return role
