from aws_cdk import aws_iotanalytics as iotanl_


def base_iot_analytics_datastore(construct, **kwargs):
    """
    Function that generates an IoT Analytics Datastore.
    :param construct: Custom construct that will use this function. From the external construct is usually 'self'.
    :param kwargs: Consist of required 'datastore_name', and optional 'retention_period'.
    :return: IoT Analytics Datastore Construct.
    """
    datastore_name = kwargs["datastore_name"].replace("-", "_")
    retention_days = kwargs.get("retention_period")
    unlimited_storage = False if retention_days is not None else True

    retention_period_property = iotanl_.CfnDatastore.RetentionPeriodProperty(
        number_of_days=retention_days, unlimited=unlimited_storage
    )
    datastore = iotanl_.CfnDatastore(
        construct, id=datastore_name, datastore_name=datastore_name, retention_period=retention_period_property
    )

    return datastore
