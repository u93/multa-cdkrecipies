from aws_cdk import aws_kinesisfirehose as fh_stream
from .bucket import base_bucket
from .role import base_kinesis_firehose_s3_role


def base_kinesis_firehose_delivery_stream(construct, **kwargs):
    # TODO: ADD ROLES, BUCKETS, AND FIREHOSE MINIMUM SETTINGS
    """
    Function that generates a Kinesis Firehose Delivery Stream.
    :param construct: Custom construct that will use this function. From the external construct is usually 'self'.
    :param kwargs: Consist of required 'stream_name'.
    :return: Kinesis Stream Construct.
    """
    stream_name = construct.prefix + "_" + kwargs["stream_name"] + "_" + "stream" + "_" + construct.environment_
    destinations_config = firehose_destinations(kwargs["destinations"])
    firehose_stream = fh_stream.CfnDeliveryStream(
        construct,
        id=stream_name,
        delivery_stream_name=stream_name,
        elasticsearch_destination_configuration=destinations_config["elasticsearch_destination_configuration"],
        extended_s3_destination_configuration=destinations_config["extended_s3_destination_configuration"],
        redshift_destination_configuration=destinations_config["redshift_destination_configuration"],
        s3_destination_configuration=destinations_config["s3_destination_configuration"],
        splunk_destination_configuration=destinations_config["splunk_destination_configuration"],
    )

    return firehose_stream.attr_arn


def firehose_destinations(configuration):
    destinations_config = dict(
        elasticsearch_destination_configuration=None,
        extended_s3_destination_configuration=None,
        redshift_destination_configuration=None,
        s3_destination_configuration=None,
        splunk_destination_configuration=None,
    )
    if configuration.get("elasticsearch_destination_configuration") is not None:
        pass
    if configuration.get("extended_s3_destination_configuration") is not None:
        bucket = base_bucket()
        role = base_kinesis_firehose_s3_role()
        extended_s3_config = fh_stream.CfnDeliveryStream.ExtendedS3DestinationConfigurationProperty(
            bucket_arn=bucket.bucket_arn,
            role_arn=role.role_arn,
            compression_format="",
            buffering_hints="",
        )
        destinations_config["extended_s3_destination_configuration"] = extended_s3_config
    if configuration.get("redshift_destination_configuration") is not None:
        pass
    if configuration.get("s3_destination_configuration") is not None:
        bucket = base_bucket()
        role = base_kinesis_firehose_s3_role()
        s3_config = fh_stream.CfnDeliveryStream.S3DestinationConfigurationProperty(
            bucket_arn=bucket.bucket_arn,
            role_arn=role.role_arn,
            compression_format="",
            buffering_hints="",
        )
        destinations_config["s3_destination_configuration"] = s3_config
    if configuration.get("splunk_destination_configuration") is not None:
        pass

    return destinations_config
