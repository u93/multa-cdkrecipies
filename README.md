# multacdkrecipies - Custom CDK Constructs for rapid development

![multacdkrecipies logo](etc/img/logo.png)

![Versions](https://img.shields.io/pypi/v/multacdkrecipies)
[![Downloads](https://pepy.tech/badge/multacdkrecipies)](https://pepy.tech/project/multacdkrecipies)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/)

 - Designed to facilitate AWS CDK usage in Python CDK Apps by creating high-level constructs that help development in Serverless Applications.
 - Designed to be used like a regular Python CDK application.
 - Designed to expose resources over Python Classes properties, keeping flexibility in the CDK application.
 - Designed to configure constructs by passing settings in Python dictionaries.


**Installation**
---

1. Install with [`pip`](https://pypi.org/project/stronghold/)
    + `$ pip install multacdkrecipies`


**Usage**
---

- `config.py`
    + Set configuration for the multacdkrecipies CDK Constructs.
```
"LAMBDA_LAYER_CONFIG": {
    "identifier": "api_gateway",
    "layer_name": "api_gateway_venv_layer",
    "description": "Lambda Layer containing local Python's Virtual Environment needed for the handler functions.",
    "layer_runtimes": ["PYTHON_3_7"],
}

API_CONFIG = {
    "api": {
        "apigateway_name": "device_gateway",
        "apigateway_description": "API Gateway used for Multa Device Agents to be associated to the AWS IoT",
        "authorizer_function": {
            "origin": {
                "lambda_name": "authorizer",
                "description": "Authorizer Lambda function for API resources.",
                "code_path": "./src/functions/",
                "runtime": "PYTHON_3_7",
                "handler": "authorizer.lambda_handler",
                "layers": [],
                "timeout": 10,
                "environment_vars": {
                    "LOG_LEVEL": "INFO",
                },
                "iam_actions": ["*"],
            }
        },
        "settings": {
            "proxy": False,
            "custom_domain": {
                "domain_name": "cvm-agent.dev.multa.io",
                "certificate_arn": "arn:aws:acm:us-east-1:112646120612:certificate/48e19da0-71a4-417a-9247-c02ef100749c",
            },
            "default_cors_options": {"allow_origins": ["*"], "options_status_code": 200},
            "default_http_methods": ["GET"],
            "default_stage_options": {"metrics_enabled": True, "logging_level": "INFO"},
            "default_handler": {
                "lambda_name": "device_default_handler",
                "description": "Handler Lambda for API Gateway root resource.",
                "code_path": "./src/functions/",
                "runtime": "PYTHON_3_7",
                "handler": "main_handler.lambda_handler",
                "layers": [],
                "timeout": 10,
                "environment_vars": {
                    "LOG_LEVEL": "INFO"
                },
                "iam_actions": ["*"],
            },
        },
        "resource_trees": [
            {
                "resource_name": "demo",
                "methods": ["POST"],
                "handler": {
                    "lambda_name": "device_gateway_handler",
                    "description": "Handler Lambda for API Gateway demo resource.",
                    "code_path": "./src/functions/",
                    "runtime": "PYTHON_3_7",
                    "handler": "demo_handler.lambda_handler",
                    "layers": [],
                    "timeout": 10,
                    "environment_vars": {
                        "LOG_LEVEL": "INFO",
                    },
                    "iam_actions": ["*"],
                },
            },
        ],
    }
}
```

- `stack.py`
    + Create the CDK App Stack by using multacdkrecipies CDK Constructs with the configuration defined above.
```
from aws_cdk import core
from multacdkrecipies import (
    AwsApiGatewayLambdaPipes,
    AwsLambdaLayerVenv,
)

from config import API_CONFIG, LAMBDA_LAYER_CONFIG

class ApiStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, config=None, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define Lambda Layer to be used by the API Resources Lambda handlers.
        self._device_gateway_api_lambdalayer = AwsLambdaLayerVenv(
            self,
            id="GatewayApiLayer-dev",
            prefix="gateway_api",
            environment="dev",
            configuration=LAMBDA_LAYER_CONFIG,
        )
        layer_arn = self._device_gateway_api_lambdalayer.lambda_layer.layer_version_arn

        # Add Lambda Layer ARN to the Lambda Functions configuration.
        API_CONFIG["api"]["authorizer_function"]["origin"]["layers"].append(layer_arn)
        API_CONFIG["api"]["settings"]["default_handler"]["layers"].append(layer_arn)
        API_CONFIG["api"]["resource_trees"]:
            function["handler"]["layers"].append(layer_arn)

        # Define Lambda Functions handlers for the API Gateway resources.
        self._gateway_api = AwsApiGatewayLambdaPipes(
            self,
            id="GatewayApiGw-dev",
            prefix="gateway_api",
            environment="dev",
            configuration=API_CONFIG,
        )
```

- `app.py`
    + Initialize the CDK App like a regular CDK App.
```
from aws_cdk import core
from stack import ApiStack

app = core.App()
ApiStack(app, id=f"GatewayApiStack-dev")

app.synth()
```


**How to Contribute**
---

1. Clone repo and create a new branch: `$ git checkout https://github.com/u93/multacdkrecipies -b ${BRANCH_NAME}`.
2. Make changes and test
3. Submit Pull Request with comprehensive description of changes

**Acknowledgements**
---

+ [@sfernandezf](https://github.com/sfernandezf) for all the help and introduce me to AWS.
+ Mauricio Villaescusa for introduce me to CDK and listen all my dummy ideas.
+ [@destradar93](https://github.com/destradar93) and [@yoya93](https://github.com/yoya93) for all the help testing and using this project.

**Donations**
---

This is free, open-source software, so no need to donate anything except knowledge... Contributions are good enough :)