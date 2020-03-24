import traceback

from aws_cdk import aws_cloudwatch as cloudwatch


def base_alarm(construct, resource_name: str, base_resource, **kwargs):
    """

    :param construct:
    :param resource_name:
    :param base_resource:
    :param kwargs:
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
