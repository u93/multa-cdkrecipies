from aws_cdk import aws_kinesis as stream
from aws_cdk.core import Duration


def base_kinesis_stream(construct, **kwargs):
    """
    Function that generates a Kinesis Data Stream.
    :param construct: Custom construct that will use this function. From the external construct is usually 'self'.
    :param kwargs: Consist of required 'stream_name'.
    :return: Kinesis Stream Construct.
    """
    stream_name = construct.prefix + "_" + kwargs["stream_name"] + "_" + "stream" + "_" + construct.environment_
    stream_retention_period = Duration.hours(kwargs["retention_period"]) if kwargs.get("retention_period") is not None else None
    kinesis_stream = stream.Stream(
        construct,
        id=stream_name,
        stream_name=stream_name,
        shard_count=kwargs["shard_count"],
        retention_period=stream_retention_period,
    )

    return kinesis_stream
