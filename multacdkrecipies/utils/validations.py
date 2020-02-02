import traceback

from schema import Schema, And, Use, Optional, SchemaError


SNS_CONFIG_SCHEMA = Schema(
    {
        "topic_name": And(Use(str)),
        "lambda_handler": {
            "lambda_name": And(Use(str)),
            Optional("description"): And(Use(str)),
            "code_path": And(Use(str)),
            "runtime": And(Use(str)),
            "handler": And(Use(str)),
            Optional("timeout"): And(Use(int)),
            Optional("reserved_concurrent_executions"): And(Use(int)),
            Optional("environment_vars"): And(Use(dict)),
        },
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
        "queue_name": And(Use(str)),
        "lambda_handler": {
            "lambda_name": And(Use(str)),
            Optional("description"): And(Use(str)),
            "code_path": And(Use(str)),
            "runtime": And(Use(str)),
            "handler": And(Use(str)),
            Optional("timeout"): And(Use(int)),
            Optional("reserved_concurrent_executions"): And(Use(int)),
            Optional("environment_vars"): And(Use(dict)),
        },
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

IOT_ANALYTICS_DATA_WORKFLOW = Schema({"name": And(Use(str))})

IOT_ANALYTICS_FAN_IN = Schema(
    {
        "channel_pipe_definition": [{"extra_activities": And(Use(list)), "name": And(Use(str))}],
        "datastore_name": And(Use(str)),
    }
)


def validate_configuration(configuration_schema, configuration_received):
    try:
        configuration_schema.validate(configuration_received)
    except SchemaError:
        print(traceback.format_exc())
        raise RuntimeError("Improper configuration passed to Multa CDK Construct!!!")
