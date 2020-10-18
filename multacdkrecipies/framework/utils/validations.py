import os
import traceback

from schema import Schema, And, Use, Optional, SchemaError

from .base_validations import (
    AUTHORIZER_LAMBDA_BASE_SCHEMA,
    DYNAMODB_TABLE_SCHEMA,
    IOT_ANALYTICS_DATASET,
    LAMBDA_BASE_SCHEMA,
    S3_BUCKET_SCHEMA,
)

APIGATEWAY_ASYNC_WEB_SERVICE_SCHEMA = Schema(
    {
        Optional("buckets"): [S3_BUCKET_SCHEMA],
        "api": {
            Optional("authorizer_function"): AUTHORIZER_LAMBDA_BASE_SCHEMA,
            "lambda_handler": {
                "resources": [{"method": And(Use(str))}],
                "handler": LAMBDA_BASE_SCHEMA,
            },
            "http_handler": {
                "resources": [{"method": And(Use(str)), "lambda_authorizer": And(Use(str))}],
                "handler": {},
            },
            "service_handler": {
                "resources": [{"method": And(Use(str)), "lambda_authorizer": And(Use(str))}],
                "handler": {},
            },
        },
    }
)

APIGATEWAY_SIMPLE_WEB_SERVICE_SCHEMA = Schema(
    {
        Optional("buckets"): [S3_BUCKET_SCHEMA],
        "api": {
            "apigateway_name": And(Use(str)),
            Optional("apigateway_description"): And(Use(str)),
            "proxy": And(Use(bool)),
            Optional("authorizer_function"): AUTHORIZER_LAMBDA_BASE_SCHEMA,
            "settings": {
                "proxy": And(Use(bool)),
                Optional("allowed_origins"): [And(Use(str))],
                Optional("custom_domain"): {"domain_name": And(Use(str)), "certificate_arn": And(Use(str))},
                Optional("default_cors_options"): {
                    "allow_origins": [And(Use(str))],
                    "options_status_code": And(Use(int)),
                },
                Optional("default_http_methods"): [And(Use(str))],
                "default_handler": LAMBDA_BASE_SCHEMA,
                Optional("default_media_types"): [And(Use(str))],
                Optional("default_stage_options"): {"metrics_enabled": And(Use(bool)), "logging_level": And(Use(str))},
            },
            "resource": {
                "resource_name": And(Use(str)),
                Optional("methods"): [And(Use(str))],
                Optional("handler"): LAMBDA_BASE_SCHEMA,
            },
        },
    }
)

APIGATEWAY_ROBUST_WEB_SERVICE_SCHEMA = Schema(
    {
        Optional("buckets"): [S3_BUCKET_SCHEMA],
        "api": {
            "apigateway_name": And(Use(str)),
            Optional("apigateway_description"): And(Use(str)),
            Optional("authorizer_function"): AUTHORIZER_LAMBDA_BASE_SCHEMA,
            "settings": {
                "proxy": And(Use(bool)),
                Optional("allowed_origins"): [And(Use(str))],
                Optional("custom_domain"): {"domain_name": And(Use(str)), "certificate_arn": And(Use(str))},
                Optional("default_cors_options"): {
                    "allow_origins": [And(Use(str))],
                    "options_status_code": And(Use(int)),
                },
                Optional("default_http_methods"): [And(Use(str))],
                "default_handler": LAMBDA_BASE_SCHEMA,
                Optional("default_media_types"): [And(Use(str))],
                Optional("default_stage_options"): {"metrics_enabled": And(Use(bool)), "logging_level": And(Use(str))},
            },
            Optional("resource_trees"): [
                {
                    "resource_name": And(Use(str)),
                    Optional("methods"): [And(Use(str))],
                    "handler": LAMBDA_BASE_SCHEMA,
                    Optional("child"): {
                        "resource_name": And(Use(str)),
                        Optional("methods"): [And(Use(str))],
                        "handler": LAMBDA_BASE_SCHEMA,
                        Optional("childs"): [
                            {
                                "resource_name": And(Use(str)),
                                Optional("methods"): [And(Use(str))],
                                "handler": LAMBDA_BASE_SCHEMA,
                            }
                        ],
                    },
                }
            ],
        },
    }
)

APIGATEWAY_FAN_OUT_WEB_SERVICE_SCHEMA = Schema(
    {
        Optional("buckets"): [S3_BUCKET_SCHEMA],
        "functions": [LAMBDA_BASE_SCHEMA],
        "api": {
            "apigateway_name": And(Use(str)),
            Optional("apigateway_description"): And(Use(str)),
            Optional("authorizer_function"): AUTHORIZER_LAMBDA_BASE_SCHEMA,
            "settings": {
                "proxy": And(Use(bool)),
                Optional("allowed_origins"): [And(Use(str))],
                Optional("custom_domain"): {"domain_name": And(Use(str)), "certificate_arn": And(Use(str))},
                Optional("default_cors_options"): {
                    "allow_origins": [And(Use(str))],
                    "options_status_code": And(Use(int)),
                },
                Optional("default_http_methods"): [And(Use(str))],
                "default_handler": LAMBDA_BASE_SCHEMA,
                Optional("default_media_types"): [And(Use(str))],
                Optional("default_stage_options"): {"metrics_enabled": And(Use(bool)), "logging_level": And(Use(str))},
            },
            "resource": {
                "resource_name": And(Use(str)),
                Optional("methods"): [And(Use(str))],
                Optional("handler"): LAMBDA_BASE_SCHEMA,
            },
        },
    }
)

USER_SERVERLESS_BACKEND_SCHEMA = Schema(
    {
        Optional("authorizer_function"): AUTHORIZER_LAMBDA_BASE_SCHEMA,
        Optional("buckets"): [S3_BUCKET_SCHEMA],
        Optional("dynamo_tables"): [DYNAMODB_TABLE_SCHEMA],
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
                    Optional("email"): {
                        "subject": And(Use(str)),
                        "body": And(Use(str)),
                        "style": And(Use(str)),
                    },
                    Optional("sms"): {
                        "body": And(Use(str)),
                    },
                },
            },
            "invitation": {
                Optional("email"): {
                    "subject": And(Use(str)),
                    "body": And(Use(str)),
                },
                Optional("sms"): {
                    "body": And(Use(str)),
                },
            },
            "sign_in": {"order": [And(Use(str))]},
            "attributes": {
                "standard": [
                    {
                        "name": And(Use(str)),
                        "mutable": And(Use(bool)),
                        "required": And(Use(bool)),
                    }
                ],
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
            Optional("app_client"): {
                "enabled": And(Use(bool)),
                "client_name": And(Use(str)),
                "generate_secret": And(Use(bool)),
                Optional("auth_flows"): {
                    Optional("admin_user_password"): And(Use(bool)),
                    Optional("custom"): And(Use(bool)),
                    Optional("refresh_token"): And(Use(bool)),
                    Optional("user_password"): And(Use(bool)),
                    Optional("user_srp"): And(Use(bool)),
                },
            },
            Optional("identity_pool"): {
                "identity_pool_name": And(Use(str)),
                Optional("allow_unauth_identities"): And(Use(bool)),
                "unauth_role": {"actions": [And(Use(str))], "resources": [And(Use(str))]},
                "auth_role": {"actions": [And(Use(str))], "resources": [And(Use(str))]},
            },
            Optional("triggers"): {
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

LAMBDA_FUNCTIONS_CLUSTER_SCHEMA = Schema(
    {
        "functions": [LAMBDA_BASE_SCHEMA],
    }
)

S3_BUCKETS_CLUSTER_SCHEMA = Schema(
    {
        "buckets": [S3_BUCKET_SCHEMA],
    }
)

S3_SPA_SIMPLE_PIPELINE_SCHEMA = Schema(
    {
        "hosting": {
            "bucket": S3_BUCKET_SCHEMA,
        },
        "pipeline": {
            "name": And(Use(str)),
            "stages": {
                Optional("github_source"): {
                    "name": And(Use(str)),
                    "branch": And(Use(str)),
                    "repo": And(Use(str)),
                    "owner": And(Use(str)),
                    "oauth_token_secret_arn": And(Use(str)),
                },
                "build": {
                    "name": And(Use(str)),
                    Optional("version"): And(Use(str)),
                    "commands": [And(Use(str))],
                    "build_directory": And(Use(str)),
                    Optional("files"): And(Use(str)),
                },
                "deploy": {
                    "name": And(Use(str)),
                },
            },
        },
    }
)

S3_SPA_SIMPLE_PIPELINE_HOSTING_SCHEMA = Schema(
    {
        "hosting": {
            "bucket": S3_BUCKET_SCHEMA,
            "cloudfront_distribution": {
                "name": And(Use(str)),
                "origin_config": {"behaviours": {"is_default_behavior": And(Use(bool))}},
            },
        },
        "pipeline": {
            "name": And(Use(str)),
            "stages": {
                Optional("github_source"): {
                    "name": And(Use(str)),
                    "branch": And(Use(str)),
                    "repo": And(Use(str)),
                    "owner": And(Use(str)),
                    "oauth_token_secret_arn": And(Use(str)),
                },
                "build": {
                    "name": And(Use(str)),
                    Optional("version"): And(Use(str)),
                    "commands": [And(Use(str))],
                    "build_directory": And(Use(str)),
                    Optional("files"): And(Use(str)),
                },
                "deploy": {
                    "name": And(Use(str)),
                },
            },
        },
    }
)

USER_POOL_GROUPS_SCHEMA = Schema(
    {
        "user_pool_groups": [
            {
                "group_name": And(Use(str)),
                Optional("description"): And(Use(str)),
                "pool_id": And(Use(str)),
                "precedence": And(Use(int)),
                "role": {
                    "name": And(Use(str)),
                    "actions": [And(Use(str))],
                    "resources": [And(Use(str))],
                    "principal": And(Use(str)),
                },
            }
        ]
    }
)

IOT_LAMBDA_CONFIG_SCHEMA = Schema(
    {
        "lambda_handler": LAMBDA_BASE_SCHEMA,
        "iot_rule": {
            "rule_name": And(Use(str)),
            Optional("description"): And(Use(str)),
            "rule_disabled": And(Use(bool)),
            "sql": And(Use(str)),
            "aws_iot_sql_version": And(Use(str)),
        },
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
            LAMBDA_BASE_SCHEMA,
        ],
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
        "lambda_handlers": [
            LAMBDA_BASE_SCHEMA,
        ],
        "iot_rule": {
            "rule_name": And(Use(str)),
            Optional("description"): And(Use(str)),
            "rule_disabled": And(Use(bool)),
            "sql": And(Use(str)),
            "aws_iot_sql_version": And(Use(str)),
        },
    }
)

CLOUDWATCH_CONFIG_SCHEMA = Schema(
    {
        "cloudwatch_rule": {
            "rule_name": And(Use(str)),
            Optional("description"): And(Use(str)),
            "enabled": And(Use(bool)),
            "schedule": And(Use(str)),
        },
        "lambda_handlers": [
            LAMBDA_BASE_SCHEMA,
        ],
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
        "lambda_handlers": [
            LAMBDA_BASE_SCHEMA,
        ],
    }
)

IOT_KINESIS_CONFIG_SCHEMA = Schema(
    {
        "stream": {
            "stream_name": And(Use(str)),
            "shard_count": And(Use(int)),
            Optional("retention_period"): And(Use(int)),
        },
        "lambda_handlers": [
            {
                "lambda_handler": LAMBDA_BASE_SCHEMA,
                "event_settings": {"starting_position": And(Use(str)), "batch_size": And(Use(int))},
            }
        ],
        "iot_rule": {
            "rule_name": And(Use(str)),
            Optional("description"): And(Use(str)),
            "rule_disabled": And(Use(bool)),
            "sql": And(Use(str)),
            "aws_iot_sql_version": And(Use(str)),
        },
    }
)

IOT_KINESIS_FIREHOSE_CONFIG_SCHEMA = Schema(
    {
        "stream": {
            "stream_name": And(Use(str)),
            "destinations": {
                Optional("extended_s3_destination_configuration"): {
                    "bucket": S3_BUCKET_SCHEMA,
                    "compression_format": And(Use(str)),
                    "buffering_hints": And(Use(str)),
                },
                Optional("s3_destination_configuration"): {
                    "bucket": S3_BUCKET_SCHEMA,
                    "compression_format": And(Use(str)),
                    "buffering_hints": And(Use(str)),
                },
            },
        },
        "iot_rule": {
            "rule_name": And(Use(str)),
            Optional("description"): And(Use(str)),
            "rule_disabled": And(Use(bool)),
            "sql": And(Use(str)),
            "aws_iot_sql_version": And(Use(str)),
        },
    }
)

IOT_ANALYTICS_DATA_WORKFLOW_SCHEMA = Schema(
    {
        "name": And(Use(str)),
        Optional("retention_periods"): {
            Optional("channel"): And(Use(int)),
            Optional("datastore"): And(Use(int)),
        },
        Optional("datasets"): [IOT_ANALYTICS_DATASET],
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
        Optional("datasets"): [IOT_ANALYTICS_DATASET],
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
        Optional("datasets"): [IOT_ANALYTICS_DATASET],
    }
)

IOT_ANALYTICS_SIMPLE_PIPELINE_SCHEMA = Schema(
    {
        "analytics_resource_name": And(Use(str)),
        Optional("retention_periods"): {
            Optional("channel"): And(Use(int)),
            Optional("datastore"): And(Use(int)),
        },
        Optional("datasets"): [IOT_ANALYTICS_DATASET],
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

IOT_POLICY_SCHEMA = Schema({"name": And(Use(str)), "policy_document": And(Use(dict))})

LAMBDA_LAYER_SCHEMA = Schema(
    {
        "identifier": And(Use(str)),
        "layer_name": And(Use(str)),
        Optional("description"): And(Use(str)),
        Optional("license"): And(Use(str)),
        Optional("dependencies"): And(Use(bool)),
        Optional("paths"): {
            "layer_code_path": And(Use(str)),
            "layer_directory_path": And(Use(str)),
            "python_requirements_file_path": And(Use(str)),
        },
        "layer_runtimes": [And(Use(str))],
        Optional("exclude"): [And(Use(str))],
    }
)

PIPELINE_SERVERLESS = Schema(
    {
        "build": {
            "project_name": And(Use(str)),
            Optional("project_description"): And(Use(str)),
            "environment_base_image": And(Use(str)),
            Optional("environment_variables"): {},
        }
    }
)

SAGEMAKER_NOTEBOOK_SCHEMA = Schema(
    {
        "name": And(Use(str)),
        "scripts": {"on_create": And(Use(str)), "on_start": And(Use(str))},
        "instance_type": And(Use(str)),
    }
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
