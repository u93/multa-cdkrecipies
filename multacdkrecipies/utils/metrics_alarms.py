import traceback

from aws_cdk import (
    core,
    aws_cloudwatch as cloudwatch,
)


class AwsCloudwatchConstructAlarm(core.Construct):
    """
    Queue Alarm Wrapper

    Attributes:
        prefix (str): The prefix set on the name of each resource created in the stack. Just for organization purposes.
        environment_ (str): The environment that all resources will use. Also for organizational and testing purposes.

    """

    def __init__(self, scope: core.Construct, id: str, *, prefix: str, environment: str, construct, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.prefix = prefix
        self.environment_ = environment
        self.construct = construct

    def __call__(self, *args, **kwargs):
        # PRE CONSTRUCT
        print("Calling class decorator")

        # CONSTRUCT
        generated_construct = self.construct()

        # POST CONSTRUCT
        construct_properties = vars(generated_construct)
        print(construct_properties)

        for property_, object_ in construct_properties.items():
            print(type(property_))
            print(type(object_))






