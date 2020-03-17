import traceback

from aws_cdk import (
    aws_sqs as sqs,
)


def base_queue_cdk(construct, **kwargs):
    queue_name = kwargs["queue_name"]
    queue_delivery_delay = kwargs.get("queue_delivery_delay")
    queue_visibility_timeout = kwargs.get("queue_visibility_timeout")
    queue = sqs.Queue(
        construct,
        id=queue_name,
        queue_name=queue_name,
        delivery_delay=queue_delivery_delay,
        visibility_timeout=queue_visibility_timeout
    )

    return queue