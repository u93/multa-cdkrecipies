import os
import traceback

from schema import Schema, And, Use, Optional, SchemaError

LAMBDA_BASE_SCHEMA = {
    "lambda_name": And(Use(str)),
    Optional("description"): And(Use(str)),
    Optional("code_path"): And(Use(str)),
    "runtime": And(Use(str)),
    "handler": And(Use(str)),
    Optional("layers"): [And(Use(str))],
    Optional("timeout"): And(Use(int)),
    Optional("reserved_concurrent_executions"): And(Use(int)),
    Optional("environment_vars"): {And(Use(str)): And(Use(str))},
    "iam_actions": [And(Use(str))],
    Optional("alarms"): [
        {
            "name": And(Use(str)),
            "number": And(Use(int)),
            "periods": And(Use(int)),
            "points": And(Use(int)),
            "actions": And(Use(bool)),
        }
    ],
}

APIGATEWAY_LAMBDA_SCHEMA = Schema(
    {
        "api": {
            "lambda_authorizer": {
                Optional("imported"): [{"lambda_arn": And(Use(str))}],
                Optional("origin"): [
                    {
                        "lambda_name": And(Use(str)),
                        Optional("description"): And(Use(str)),
                        Optional("code_path"): And(Use(str)),
                        "runtime": And(Use(str)),
                        "handler": And(Use(str)),
                        Optional("timeout"): And(Use(int)),
                        Optional("reserved_concurrent_executions"): And(Use(int)),
                        Optional("environment_vars"): {And(Use(str)): And(Use(str))},
                        "iam_actions": [And(Use(str))],
                        Optional("alarms"): [
                            {
                                "name": And(Use(str)),
                                "number": And(Use(int)),
                                "periods": And(Use(int)),
                                "points": And(Use(int)),
                                "actions": And(Use(bool)),
                            }
                        ],
                    }
                ],
            },
            "lambda_handler": {
                "resources": [{"method": And(Use(str))}],
                "handler": {
                    "lambda_name": And(Use(str)),
                    Optional("description"): And(Use(str)),
                    Optional("code_path"): And(Use(str)),
                    "runtime": And(Use(str)),
                    "handler": And(Use(str)),
                    Optional("timeout"): And(Use(int)),
                    Optional("reserved_concurrent_executions"): And(Use(int)),
                    Optional("environment_vars"): {And(Use(str)): And(Use(str))},
                    "iam_actions": [And(Use(str))],
                    Optional("alarms"): [
                        {
                            "name": And(Use(str)),
                            "number": And(Use(int)),
                            "periods": And(Use(int)),
                            "points": And(Use(int)),
                            "actions": And(Use(bool)),
                        }
                    ],
                },
            },
            "http_handler": {"resources": [{"method": And(Use(str)), "lambda_authorizer": And(Use(str))}], "handler": {}},
            "service_handler": {"resources": [{"method": And(Use(str)), "lambda_authorizer": And(Use(str))}], "handler": {}},
        }
    }
)

APIGATEWAY_LAMBDA_SIMPLE_WEB_SERVICE_SCHEMA = Schema(
    {
        "api": {
            "apigateway_name": And(Use(str)),
            Optional("apigateway_description"): And(Use(str)),
            "proxy": And(Use(bool)),
            "lambda_authorizer": {
                Optional("imported"): {"lambda_arn": And(Use(str)),},
                Optional("origin"): {
                    "lambda_name": And(Use(str)),
                    Optional("description"): And(Use(str)),
                    Optional("code_path"): And(Use(str)),
                    "runtime": And(Use(str)),
                    Optional("layers"): [And(Use(str))],
                    "handler": And(Use(str)),
                    Optional("timeout"): And(Use(int)),
                    Optional("reserved_concurrent_executions"): And(Use(int)),
                    Optional("environment_vars"): {And(Use(str)): And(Use(str))},
                    "iam_actions": [And(Use(str))],
                },
                Optional("alarms"): [
                    {
                        "name": And(Use(str)),
                        "number": And(Use(int)),
                        "periods": And(Use(int)),
                        "points": And(Use(int)),
                        "actions": And(Use(bool)),
                    }
                ],
            },
            "resource": {
                "name": And(Use(str)),
                Optional("allowed_origins"): [And(Use(str))],
                Optional("custom_domain"): {"domain_name": And(Use(str)), "certificate_arn": And(Use(str))},
                Optional("methods"): [And(Use(str))],
                "handler": {
                    Optional("imported"): {
                        "lambda_arn": And(Use(str)),
                        Optional("alarms"): [
                            {
                                "name": And(Use(str)),
                                "number": And(Use(int)),
                                "periods": And(Use(int)),
                                "points": And(Use(int)),
                                "actions": And(Use(bool)),
                            }
                        ],
                    },
                    Optional("origin"): {
                        "lambda_name": And(Use(str)),
                        Optional("description"): And(Use(str)),
                        Optional("code_path"): And(Use(str)),
                        Optional("layers"): [And(Use(str))],
                        "runtime": And(Use(str)),
                        "handler": And(Use(str)),
                        Optional("timeout"): And(Use(int)),
                        Optional("reserved_concurrent_executions"): And(Use(int)),
                        Optional("environment_vars"): {And(Use(str)): And(Use(str))},
                        "iam_actions": [And(Use(str))],
                    },
                    Optional("alarms"): [
                        {
                            "name": And(Use(str)),
                            "number": And(Use(int)),
                            "periods": And(Use(int)),
                            "points": And(Use(int)),
                            "actions": And(Use(bool)),
                        }
                    ],
                },
            },
        }
    }
)

SNS_CONFIG_SCHEMA = Schema(
    {
        "topic": {
            "topic_name": And(Use(str)),
            Optional("alarms"): [
                {
                    "name": And(Use(str)),
                    "number": And(Use(int)),
                    "periods": And(Use(int)),
                    "points": And(Use(int)),
                    "actions": And(Use(bool)),
                }
            ],
        },
        "lambda_handlers": [LAMBDA_BASE_SCHEMA],
    }
)

IOT_SNS_CONFIG_SCHEMA = Schema(
    {
        "topic": {
            "topic_name": And(Use(str)),
            Optional("alarms"): [
                {
                    "name": And(Use(str)),
                    "number": And(Use(int)),
                    "periods": And(Use(int)),
                    "points": And(Use(int)),
                    "actions": And(Use(bool)),
                }
            ],
        },
        "lambda_handlers": [LAMBDA_BASE_SCHEMA,],
        "iot_rule": {
            "rule_name": And(Use(str)),
            Optional("description"): And(Use(str)),
            "rule_disabled": And(Use(bool)),
            "sql": And(Use(str)),
            "aws_iot_sql_version": And(Use(str)),
        },
    }
)


IOT_SQS_CONFIG_SCHEMA = Schema(
    {
        "queue": {
            "queue_name": And(Use(str)),
            Optional("queue_delivery_delay"): And(Use(int)),
            Optional("queue_message_visibility"): And(Use(int)),
            Optional("alarms"): [
                {
                    "name": And(Use(str)),
                    "number": And(Use(int)),
                    "periods": And(Use(int)),
                    "points": And(Use(int)),
                    "actions": And(Use(bool)),
                }
            ],
        },
        "lambda_handlers": [LAMBDA_BASE_SCHEMA,],
        "iot_rule": {
            "rule_name": And(Use(str)),
            Optional("description"): And(Use(str)),
            "rule_disabled": And(Use(bool)),
            "sql": And(Use(str)),
            "aws_iot_sql_version": And(Use(str)),
        },
    }
)

SQS_CONFIG_SCHEMA = Schema(
    {
        "queue": {
            "queue_name": And(Use(str)),
            Optional("queue_delivery_delay"): And(Use(int)),
            Optional("queue_message_visibility"): And(Use(int)),
            Optional("alarms"): [
                {
                    "name": And(Use(str)),
                    "number": And(Use(int)),
                    "periods": And(Use(int)),
                    "points": And(Use(int)),
                    "actions": And(Use(bool)),
                }
            ],
        },
        "lambda_handlers": [LAMBDA_BASE_SCHEMA,],
    }
)

IOT_ANALYTICS_DATA_WORKFLOW_SCHEMA = Schema({"name": And(Use(str))})

IOT_ANALYTICS_FAN_IN_SCHEMA = Schema(
    {"channel_pipe_definition": [{"extra_activities": And(Use(list)), "name": And(Use(str))}], "datastore_name": And(Use(str)),}
)

IOT_ANALYTICS_FAN_OUT_SCHEMA = Schema(
    {"datastore_pipe_definition": [{"extra_activities": And(Use(list)), "name": And(Use(str))}], "channel_name": And(Use(str)),}
)

IOT_ANALYTICS_SIMPLE_PIPELINE = Schema(
    {
        "analytics_resource_name": And(Use(str)),
        "iot_rule": {
            "rule_name": And(Use(str)),
            Optional("description"): And(Use(str)),
            "rule_disabled": And(Use(bool)),
            "sql": And(Use(str)),
            "aws_iot_sql_version": And(Use(str)),
        },
    }
)

IOT_POLICY = Schema({"name": And(Use(str)), "policy_document": And(Use(dict))})

LAMBDA_LAYER_SCHEMA = Schema(
    {
        "layer_name": And(Use(str)),
        Optional("description"): And(Use(str)),
        Optional("license"): And(Use(str)),
        Optional("paths"): {
            "python_requirements_path": And(Use(str)),
            "layer_directory_path": And(Use(str)),
            "layer_code_path": And(Use(str)),
        },
        "layer_runtimes": [And(Use(str))],
        Optional("exclude"): [And(Use(str))],
    }
)

SAGEMAKER_NOTEBOOK_SCHEMA = Schema(
    {"name": And(Use(str)), "scripts": {"on_create": And(Use(str)), "on_start": And(Use(str))}, "instance_type": And(Use(str)),}
)

SSM_PARAMETER_STRING_SCHEMA = Schema(
    {"name": And(Use(str)), Optional("description"): And(Use(str)), "string_value": And(Use(dict))}
)


def validate_configuration(configuration_schema, configuration_received):
    """
    Validates the configuration passed to CDK Constructs.
    :param configuration_schema: Base Multa Recipe Schema in the project.
    :param configuration_received: Configuration passed by external application.
    """
    try:
        configuration_schema.validate(configuration_received)
    except SchemaError:
        print("Improper configuration passed to Multa CDK Construct!!!")
        print(traceback.format_exc())
        raise RuntimeError


def validate_file(file_path: str):
    """
    Validates if file exists
    :param file_path: Full path to the file that wants to be validated.
    :return: True or False depending if the file exists or don't.
    """
    return os.path.isfile(file_path)
