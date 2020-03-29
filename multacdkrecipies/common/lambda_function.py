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
    Function that generates a Lambda Function. Using the parameter 'code_path' it gets the code from a path set for
    the user or a preset path. The function gets all the allowed IAM actions and will have access to all resources for
    a matter of simplicity.
    :param construct: Custom construct that will use this function. From the external construct is usually 'self'.
    :param kwargs: Consist of required 'lambda_name', 'handler', 'runtime', 'iam_actions' and optionals 'code_path', 'description', 'environment_vars', 'timeout', 'reserved_concurrent_executions'.
    :return: Lambda Function Construct.
    """
    try:
        function_runtime = getattr(lambda_.Runtime, kwargs["runtime"])
    except Exception:
        print(f"Wrong function runtime {kwargs['runtime']} specified")
        raise WrongRuntimePassed(tb=traceback.format_exc())

    obtainer_code_path = kwargs.get("code_path")
    if obtainer_code_path is not None:
        code_path = obtainer_code_path
    elif obtainer_code_path is None and DEFAULT_LAMBDA_CODE_PATH_EXISTS is True:
        code_path = DEFAULT_LAMBDA_CODE_PATH
    else:
        print(f"Code path for Lambda Function {kwargs['lambda_name']} is not valid!")
        raise RuntimeError

    function_layers = list()
    for layer_arn in kwargs.get("layers", list()):
        try:
            layer = lambda_.LayerVersion.from_layer_version_arn(construct, id=layer_arn, layer_version_arn=layer_arn)
        except Exception:
            print(f"Error using Lambda Layer ARN {layer_arn}")
            raise RuntimeError
        else:
            function_layers.append(layer)

    # Defining Lambda function
    _lambda_function = lambda_.Function(
        construct,
        id=construct.prefix + "_" + kwargs["lambda_name"] + "_" + construct.environment_,
        function_name=construct.prefix + "_" + kwargs["lambda_name"] + "_" + construct.environment_,
        code=lambda_.Code.from_asset(path=code_path),
        handler=kwargs["handler"],
        runtime=function_runtime,
        layers=function_layers,
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
