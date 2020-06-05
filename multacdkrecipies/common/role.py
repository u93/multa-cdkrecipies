import traceback

from aws_cdk import aws_iam as iam, core


def base_role(construct, resource_name: str, principal_resource: str, actions: list, resources: list):
    """
    Function that generates an IAM Role with a Policy.
    :param construct: Custom construct that will use this function. From the external construct is usually 'self'.
    :param resource_name: Name of the resource. Used for naming purposes.
    :param principal_resource: Resource used to define a Service Principal. Has to match an AWS Resource. For example, 'iot' -> 'iot.amazonaws.com'.
    :param actions: Action list containing AWS IAM defined actions. For example 'sns:Publish'
    :param resources: List of resources ARNs defined by AWS.
    :return: IAM Role with an IAM Policy attached.
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
        role = base_role(construct, resource_name, principal_resource, actions=actions, resources=resources)
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
        role = base_role(construct, resource_name, principal_resource, actions=actions, resources=resources)
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
        role = base_role(construct, resource_name, principal_resource, actions=actions, resources=resources)
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
        role = base_role(construct, resource_name, principal_resource, actions=actions, resources=resources)
    except Exception:
        print(traceback.format_exc())
    else:
        return role


def base_iot_analytics_role(construct, resource_name: str, principal_resource: str, **kwargs):
    """
    Function that generates an IAM Role with a Policy for SQS Send Message.
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
        role = base_role(construct, resource_name, principal_resource, actions=actions, resources=resources)
    except Exception:
        print(traceback.format_exc())
    else:
        return role
