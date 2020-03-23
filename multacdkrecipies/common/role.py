import traceback

from aws_cdk import (
    aws_iam as iam,
)


def base_role(construct, resource_name: str, principal_resource: str, actions, resources):
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


def base_sns_role(construct, resource_name: str, principal_resource: str, **kwargs):
    """
    No base_resource is required because the high level of customization, just base_resoruce is enough.
    Instead we use specific functions to accommodate the role creation for specific resources.
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
    No base_resource is required because the high level of customization, just base_resoruce is enough.
    Instead we use specific functions to accommodate the role creation for specific resources.
    """
    try:
        actions = ["sqs:SendMessage"]
        resources = [construct._sqs_queue.queue_arn]
        role = base_role(construct, resource_name, principal_resource, actions=actions, resources=resources)
    except Exception:
        print(traceback.format_exc())
    else:
        return role
