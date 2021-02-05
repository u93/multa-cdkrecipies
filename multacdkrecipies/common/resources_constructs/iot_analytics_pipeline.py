from aws_cdk import aws_iotanalytics as iotanl_


def channel_activity(resource, next_resource):
    channel_activity_property = iotanl_.CfnPipeline.ChannelProperty(
        channel_name=resource.channel_name,
        name=resource.channel_name,
        next=next_resource.datastore_name,
    )
    pipeline_channel_activity = iotanl_.CfnPipeline.ActivityProperty(channel=channel_activity_property)
    return pipeline_channel_activity


def datastore_activity(resource):
    datastore_activity_property = iotanl_.CfnPipeline.DatastoreProperty(
        datastore_name=resource.datastore_name, name=resource.datastore_name
    )
    pipeline_datastore_activity = iotanl_.CfnPipeline.ActivityProperty(datastore=datastore_activity_property)
    return pipeline_datastore_activity


def base_iot_analytics_pipeline(construct, activities: dict, resource_dependencies: list, **kwargs):
    """
    Function that generates an IoT Analytics Pipeline.
    :param construct: Custom construct that will use this function. From the external construct is usually 'self'.
    :param activities: Analytics Pipeline activities, required are Channel and Datastore ones passed as dictionary.
    :param resource_dependencies: List of resources dependencies required for CloudFormation, usually a Channel and a Datastore resources.
    :param kwargs: Consist of required 'pipeline_name'.
    :return: IoT Analytics Pipeline Construct.
    """
    pipeline_name = kwargs["pipeline_name"].replace("-", "_")
    _channel_activity = channel_activity(resource=activities["channel"], next_resource=activities["datastore"])
    _datastore_activity = datastore_activity(resource=activities["datastore"])

    pipeline_activities = list()
    pipeline_activities.append(_channel_activity)
    pipeline_activities.append(_datastore_activity)

    pipeline = iotanl_.CfnPipeline(
        construct, id=pipeline_name, pipeline_name=pipeline_name, pipeline_activities=pipeline_activities
    )
    for dependency in resource_dependencies:
        pipeline.add_depends_on(target=dependency)

    return pipeline
