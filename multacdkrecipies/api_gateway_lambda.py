import traceback

from aws_cdk import (
    core,
    aws_apigateway as api_gateway,
    aws_cloudwatch as cloudwatch,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_sns as sns,
    aws_sns_subscriptions as sns_subs,
)


