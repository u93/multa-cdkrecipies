import traceback

from aws_cdk import aws_cloudwatch as cloudwatch


def base_alarm(construct, resource_name: str, base_resource, **kwargs):
    """
    Function that generates a Cloudwatch Alarm.
    :param construct: Custom construct that will use this function. From the external construct is usually 'self'.
    :param resource_name: The resource that the Alarm is generated for. Used for naming purposes.
    :param base_resource: Resource construct object from which the metrics will be generated.
    :param kwargs: Consist of required 'name' (name of the metric according to CDK), 'number' (value to compare the metrics), 'periods'(compared periods) 'points' (points to alarm), 'actions_enabled' (enable or not actions).
    :return:
    """
    try:
        alarm = cloudwatch.Alarm(
            construct,
            id=construct.prefix + "_" + resource_name + "_" + kwargs["name"] + "_" + construct.environment_,
            alarm_name=construct.prefix + "_" + resource_name + "_" + kwargs["name"] + "_" + construct.environment_,
            metric=base_resource.metric(kwargs["name"]),
            threshold=kwargs["number"],
            evaluation_periods=kwargs["periods"],
            datapoints_to_alarm=kwargs["points"],
            actions_enabled=kwargs["actions"],
        )
    except Exception:
        print(traceback.format_exc())
    else:
        return alarm
