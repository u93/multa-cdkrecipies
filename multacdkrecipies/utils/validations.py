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

USER_POOL_DYNAMODB_SCHEMA = Schema(
    {
        "organization": {
            "table_name": And(Use(str)),
            "partition_key": And(Use(str)),
            Optional("sort_key"): {"name": And(Use(str)), "type": And(Use(str)),},
            Optional("stream"): {"enabled": And(Use(bool)), Optional("function"): LAMBDA_BASE_SCHEMA},
            Optional("ttl_attribute"): And(Use(str)),
            Optional("billing_mode"): And(Use(str)),
            Optional("read_capacity"): And(Use(str)),
            Optional("write_capacity"): And(Use(str)),
        },
        "users_attributes": {
            "table_name": And(Use(str)),
            "partition_key": And(Use(str)),
            Optional("sort_key"): And(Use(str)),
            Optional("stream"): {"enabled": And(Use(bool)), Optional("function"): LAMBDA_BASE_SCHEMA},
            Optional("ttl_attribute"): And(Use(str)),
            Optional("billing_mode"): And(Use(str)),
            Optional("read_capacity"): And(Use(str)),
            Optional("write_capacity"): And(Use(str)),
        },
        "user_pool": {
            "pool_name": And(Use(str)),
            Optional("email"): {"from": And(Use(str)), Optional("reply_to"): And(Use(str))},
            "password_policy": {
                Optional("minimum_length"): And(Use(int)),
                Optional("temporary_password_duration"): And(Use(int)),
                Optional("require"): {
                    Optional("lower_case"): And(Use(bool)),
                    Optional("upper_case"): And(Use(bool)),
                    Optional("digits"): And(Use(bool)),
                    Optional("symbols"): And(Use(bool)),
                },
            },
            "sign_up": {
                "enabled": And(Use(bool)),
                "user_verification": {
                    Optional("email"): {"subject": And(Use(str)), "body": And(Use(str)), "style": And(Use(str)),},
                    Optional("sms"): {"body": And(Use(str)),},
                },
            },
            "invitation": {
                Optional("email"): {"subject": And(Use(str)), "body": And(Use(str)),},
                Optional("sms"): {"body": And(Use(str)),},
            },
            "sign_in": {"order": [And(Use(str))]},
            "attributes": {
                "standard": [And(Use(str))],
                Optional("custom"): [
                    {
                        "name": And(Use(str)),
                        "type": And(Use(str)),
                        Optional("mutable"): And(Use(bool)),
                        Optional("minimum_length"): And(Use(int)),
                        Optional("maximum_length"): And(Use(int)),
                    }
                ],
            },
            "triggers": {
                Optional("create_auth_challenge"): LAMBDA_BASE_SCHEMA,
                Optional("custom_message"): LAMBDA_BASE_SCHEMA,
                Optional("define_auth_challenge"): LAMBDA_BASE_SCHEMA,
                Optional("post_authentication"): LAMBDA_BASE_SCHEMA,
                Optional("post_confirmation"): LAMBDA_BASE_SCHEMA,
                Optional("pre_authentication"): LAMBDA_BASE_SCHEMA,
                Optional("pre_sign_up"): LAMBDA_BASE_SCHEMA,
                Optional("pre_token_generation"): LAMBDA_BASE_SCHEMA,
                Optional("user_migration"): LAMBDA_BASE_SCHEMA,
                Optional("verify_auth_challenge_response"): LAMBDA_BASE_SCHEMA,
            },
        },
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

IOT_ANALYTICS_DATA_WORKFLOW_SCHEMA = Schema(
    {
        "name": And(Use(str)),
        Optional("retention_periods"): {Optional("channel"): And(Use(int)), Optional("datastore"): And(Use(int)),},
    }
)

IOT_ANALYTICS_FAN_IN_SCHEMA = Schema(
    {
        "channel_pipe_definition": [
            {
                Optional("extra_activities"): And(Use(list)),
                "name": And(Use(str)),
                Optional("channel_retention_period"): And(Use(int)),
            }
        ],
        "datastore_definition": {"name": And(Use(str)), Optional("datastore_retention_period"): And(Use(int))},
    }
)

IOT_ANALYTICS_FAN_OUT_SCHEMA = Schema(
    {
        "channel_definition": {"name": And(Use(str)), Optional("channel_retention_period"): And(Use(int))},
        "datastore_pipe_definition": [
            {
                Optional("extra_activities"): And(Use(list)),
                "name": And(Use(str)),
                Optional("datastore_retention_period"): And(Use(int)),
            }
        ],
    }
)

IOT_ANALYTICS_SIMPLE_PIPELINE = Schema(
    {
        "analytics_resource_name": And(Use(str)),
        Optional("retention_periods"): {Optional("channel"): And(Use(int)), Optional("datastore"): And(Use(int)),},
        "iot_rules": [
            {
                "rule_name": And(Use(str)),
                Optional("description"): And(Use(str)),
                "rule_disabled": And(Use(bool)),
                "sql": And(Use(str)),
                "aws_iot_sql_version": And(Use(str)),
            },
        ],
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
