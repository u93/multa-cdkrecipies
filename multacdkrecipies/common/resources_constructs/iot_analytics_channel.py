from aws_cdk import aws_iotanalytics as iotanl_


def base_iot_analytics_channel(construct, **kwargs):
    """
    Function that generates an IoT Analytics Channel.
    :param construct: Custom construct that will use this function. From the external construct is usually 'self'.
    :param kwargs: Consist of required 'channel_name', and optional 'retention_period'.
    :return: IoT Analytics Channel Construct.
    """
    channel_name = kwargs["channel_name"].replace("-", "_")
    retention_days = kwargs.get("retention_period")
    unlimited_storage = False if retention_days is not None else True

    retention_period_property = iotanl_.CfnChannel.RetentionPeriodProperty(
        number_of_days=retention_days, unlimited=unlimited_storage
    )
    channel = iotanl_.CfnChannel(
        construct, id=channel_name, channel_name=channel_name, retention_period=retention_period_property
    )

    return channel
