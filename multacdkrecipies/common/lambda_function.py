import traceback

from aws_cdk import (
    core,
    aws_iam as iam,
    aws_lambda as lambda_,
)

from ..settings import DEFAULT_LAMBDA_CODE_PATH, DEFAULT_LAMBDA_CODE_PATH_EXISTS
from ..utils import WrongRuntimePassed


def base_lambda_function(construct, **kwargs):
    """

    :param construct:
    :param kwargs:
    :return:
    """
    try:
        function_runtime = getattr(lambda_.Runtime, kwargs["runtime"])
    except Exception:
        raise WrongRuntimePassed(detail=f"Wrong function runtime {kwargs['runtime']} specified", tb=traceback.format_exc())

    obtainer_code_path = kwargs.get("code_path")
    if obtainer_code_path is not None:
        code_path = obtainer_code_path
    elif obtainer_code_path is None and DEFAULT_LAMBDA_CODE_PATH_EXISTS is True:
        code_path = DEFAULT_LAMBDA_CODE_PATH
    else:
        raise RuntimeError(f"Code path for Lambda Function {kwargs['lambda_name']} is not valid!")

    # Defining Lambda function
    _lambda_function = lambda_.Function(
        construct,
        id=construct.prefix + "_" + kwargs["lambda_name"] + "_lambda_" + construct.environment_,
        function_name=construct.prefix + "_" + kwargs["lambda_name"] + "_lambda_" + construct.environment_,
        code=lambda_.Code.from_asset(path=code_path),
        handler=kwargs["handler"],
        runtime=function_runtime,
        layers=None,
        description=kwargs.get("description"),
        tracing=lambda_.Tracing.ACTIVE,
        environment=kwargs.get("environment_vars"),
        timeout=core.Duration.seconds(kwargs.get("timeout")),
        reserved_concurrent_executions=kwargs.get("reserved_concurrent_executions"),
    )

    # Defining Lambda Function IAM policies to access other services
    construct.iam_policies = list()
    for iam_actions in kwargs["iam_actions"]:
        construct.iam_policies.append(iam_actions)

    policy_statement = iam.PolicyStatement(actions=construct.iam_policies, resources=["*"])
    _lambda_function.add_to_role_policy(statement=policy_statement)

    return _lambda_function
