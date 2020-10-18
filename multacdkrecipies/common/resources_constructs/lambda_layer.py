import traceback

from aws_cdk import aws_lambda as lambda_

from multacdkrecipies.recipies.settings import DEFAULT_LAMBDA_LAYER_CODE_PATH, DEFAULT_LAMBDA_LAYER_CODE_PATH_EXISTS
from multacdkrecipies.recipies.utils import WrongRuntimePassed


def base_lambda_layer(construct, **kwargs):
    """
    Function that generates a Lambda Layer. Using the parameter 'layer_code_path' it gets the code from a path set for
    the user or a preset path.
    :param construct: Custom construct that will use this function. From the external construct is usually 'self'.
    :param kwargs: Consist of required 'layer_name', 'layer_runtimes', and optionals 'layer_code_path', 'description', 'license'.
    :return: Lambda Layer Construct.
    """
    layer_runtimes = list()
    for runtime in kwargs["layer_runtimes"]:
        try:
            layer_runtime = getattr(lambda_.Runtime, runtime)
        except Exception:
            raise WrongRuntimePassed(detail=f"Wrong function runtime {runtime} specified", tb=traceback.format_exc())
        else:
            layer_runtimes.append(layer_runtime)

    obtainer_code_path = kwargs.get("layer_code_path")
    if obtainer_code_path is not None:
        layer_code_path = obtainer_code_path
    elif obtainer_code_path is None and DEFAULT_LAMBDA_LAYER_CODE_PATH_EXISTS is True:
        layer_code_path = DEFAULT_LAMBDA_LAYER_CODE_PATH
    else:
        print(f"Code path for Lambda Function {kwargs['layer_name']} is not valid!")
        raise RuntimeError

    # Defining Lambda Layer
    _lambda_layer = lambda_.LayerVersion(
        construct,
        id=construct.prefix + "_" + kwargs["layer_name"] + "_" + construct.environment_,
        layer_version_name=construct.prefix + "_" + kwargs["layer_name"] + "_" + construct.environment_,
        description=kwargs.get("description"),
        code=lambda_.Code.from_asset(path=layer_code_path, exclude=kwargs.get("exclude", ["aws_cdk"])),
        compatible_runtimes=layer_runtimes,
        license=kwargs.get("license"),
    )

    return _lambda_layer
