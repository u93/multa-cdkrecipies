from .alarms import base_alarm
from .bucket import base_bucket
from .cognito_user_groups import base_cognito_user_groups
from .cognito_user_identity_pool import base_cognito_user_identity_pool, base_cognito_user_identity_pool_attach_role
from .cognito_user_pool import base_cognito_user_pool
from .dynamo_table import base_dynamodb_table
from .iot_analytics_channel import base_iot_analytics_channel
from .iot_analytics_sql_dataset import base_iot_analytics_dataset
from .iot_analytics_datastore import base_iot_analytics_datastore
from .iot_analytics_pipeline import base_iot_analytics_pipeline
from .iot_rule import base_iot_rule
from .kinesis_firehose_delivery_stream import base_kinesis_firehose_delivery_stream, base_kinesis_firehose_s3_role
from .kinesis_stream import base_kinesis_stream
from .lambda_function import base_lambda_function
from .lambda_layer import base_lambda_layer
from .role import (
    base_cognito_identity_pool_unauth_role,
    base_cognito_identity_pool_auth_role,
    base_federated_role,
    base_service_role,
    base_iot_analytics_role,
    base_kinesis_role,
    base_kinesis_firehose_role,
    base_kinesis_firehose_s3_role,
    base_lambda_role,
    base_sns_role,
    base_sqs_role,
)
from .queue import base_queue
from .topic import base_topic
