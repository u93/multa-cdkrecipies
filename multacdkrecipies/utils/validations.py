import os
import traceback

from schema import Schema, And, Use, Optional, SchemaError


APIGATEWAY_LAMBDA_SCHEMA = Schema(
    {
        "api": {
            "lambda_authorizer": {
                "imported": [
                    {
                        "lambda_arn": And(Use(str))
                    }
                ],
                "origin": [
                    {
                        "lambda_name": And(Use(str)),
                        Optional("description"): And(Use(str)),
                        Optional("code_path"): And(Use(str)),
                        "runtime": And(Use(str)),
                        "handler": And(Use(str)),
                        Optional("timeout"): And(Use(int)),
                        Optional("reserved_concurrent_executions"): And(Use(int)),
                        Optional("environment_vars"): And(Use(dict)),
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
                ]
            },
            "lambda_handler": {
                "resources": [
                    {
                        "method": And(Use(str)),
                        "lambda_authorizer": And(Use(str))
                    }
                ],
                "handler": {
                    "lambda_name": And(Use(str)),
                    Optional("description"): And(Use(str)),
                    Optional("code_path"): And(Use(str)),
                    "runtime": And(Use(str)),
                    "handler": And(Use(str)),
                    Optional("timeout"): And(Use(int)),
                    Optional("reserved_concurrent_executions"): And(Use(int)),
                    Optional("environment_vars"): And(Use(dict)),
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
            },
            "http_handler": {
                "resources": [
                    {
                        "method": And(Use(str)),
                        "lambda_authorizer": And(Use(str))
                    }
                ],
                "handler": {}
            },
            "service_handler": {
                "resources": [
                    {
                        "method": And(Use(str)),
                        "lambda_authorizer": And(Use(str))
                    }
                ],
                "handler": {}
            }
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
        "lambda_handlers": [
            {
                "lambda_name": And(Use(str)),
                Optional("description"): And(Use(str)),
                Optional("code_path"): And(Use(str)),
                "runtime": And(Use(str)),
                "handler": And(Use(str)),
                Optional("timeout"): And(Use(int)),
                Optional("reserved_concurrent_executions"): And(Use(int)),
                Optional("environment_vars"): And(Use(dict)),
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
        ],
        "iam_actions": And(Use(list))
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
        "lambda_handlers": [
            {
                "lambda_name": And(Use(str)),
                Optional("description"): And(Use(str)),
                Optional("code_path"): And(Use(str)),
                "runtime": And(Use(str)),
                "handler": And(Use(str)),
                Optional("timeout"): And(Use(int)),
                Optional("reserved_concurrent_executions"): And(Use(int)),
                Optional("environment_vars"): And(Use(dict)),
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
        ],
        "iam_actions": And(Use(list)),
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
        "lambda_handlers": [
            {
                "lambda_name": And(Use(str)),
                Optional("description"): And(Use(str)),
                Optional("code_path"): And(Use(str)),
                "runtime": And(Use(str)),
                "handler": And(Use(str)),
                Optional("timeout"): And(Use(int)),
                Optional("reserved_concurrent_executions"): And(Use(int)),
                Optional("environment_vars"): And(Use(dict)),
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
        ],
        "iam_actions": And(Use(list)),
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
        "lambda_handlers": [
            {
                "lambda_name": And(Use(str)),
                Optional("description"): And(Use(str)),
                Optional("code_path"): And(Use(str)),
                "runtime": And(Use(str)),
                "handler": And(Use(str)),
                Optional("timeout"): And(Use(int)),
                Optional("reserved_concurrent_executions"): And(Use(int)),
                Optional("environment_vars"): And(Use(dict)),
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
        ],
        "iam_actions": And(Use(list)),
    }
)

IOT_ANALYTICS_DATA_WORKFLOW = Schema({"name": And(Use(str))})

IOT_ANALYTICS_FAN_IN = Schema(
    {"channel_pipe_definition": [{"extra_activities": And(Use(list)), "name": And(Use(str))}], "datastore_name": And(Use(str)),}
)

IOT_ANALYTICS_FAN_OUT = Schema(
    {"datastore_pipe_definition": [{"extra_activities": And(Use(list)), "name": And(Use(str))}], "channel_name": And(Use(str)),}
)

SAGEMAKER_NOTEBOOK = Schema(
    {"name": And(Use(str)), "scripts": {"on_create": And(Use(str)), "on_start": And(Use(str))}, "instance_type": And(Use(str)),}
)




def validate_configuration(configuration_schema, configuration_received):
    try:
        configuration_schema.validate(configuration_received)
    except SchemaError:
        print(traceback.format_exc())
        raise RuntimeError("Improper configuration passed to Multa CDK Construct!!!")


def validate_file(file_path: str):
    return os.path.isfile(file_path)
