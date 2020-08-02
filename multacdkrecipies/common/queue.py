from aws_cdk import aws_sqs as sqs


def base_queue(construct, **kwargs):
    """
    Function that generates an SQS Queue.
    :param construct: Custom construct that will use this function. From the external construct is usually 'self'.
    :param kwargs: Consist of required 'queue_name' and optionals 'queue_delivery_delay' and 'queue_visibility_timeout'.
    :return: SQS Queue Construct.
    """
    queue_name = construct.prefix + "_" + kwargs["queue_name"] + "_queue_" + construct.environment_
    queue_delivery_delay = kwargs.get("queue_delivery_delay")
    queue_visibility_timeout = kwargs.get("queue_visibility_timeout")
    queue = sqs.Queue(
        construct,
        id=queue_name,
        queue_name=queue_name,
        delivery_delay=queue_delivery_delay,
        visibility_timeout=queue_visibility_timeout,
    )

    return queue
