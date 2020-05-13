from schema import Schema, And, Use, Optional

LAMBDA_BASE_SCHEMA = Schema(
    {
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
)

AUTHORIZER_LAMBDA_BASE_SCHEMA = Schema(
    {Optional("origin"): LAMBDA_BASE_SCHEMA, Optional("imported"): {"arn": And(Use(str)), "identifier": And(Use(str)),}}
)

DYNAMODB_TABLE_SCHEMA = Schema(
    {
        "table_name": And(Use(str)),
        "partition_key": And(Use(str)),
        Optional("sort_key"): {"name": And(Use(str)), "type": And(Use(str)),},
        Optional("stream"): {"enabled": And(Use(bool)), Optional("function"): LAMBDA_BASE_SCHEMA},
        Optional("ttl_attribute"): And(Use(str)),
        Optional("billing_mode"): And(Use(str)),
        Optional("read_capacity"): And(Use(str)),
        Optional("write_capacity"): And(Use(str)),
    }
)
