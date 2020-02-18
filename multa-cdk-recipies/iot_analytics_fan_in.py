from aws_cdk import (
    core,
    aws_iotanalytics as analytics,
)

from .utils import IOT_ANALYTICS_FAN_IN, validate_configuration


class AwsIotAnalyticsFanIn(core.Construct):
    """
    AWS CDK Construct that defines a pipe where a Rules captures an MQTT Message sent to or from AWS IoT MQTT Broker,
    then the message is sent to an SQS Queue and a Lambda function subscribed to the topic can process it and take
    proper actions. The construct takes a few inputs.

    Attributes:
        prefix (str): The prefix set on the name of each resource created in the stack. Just for organization purposes.
        environment_ (str): The environment that all resources will use. Also for organizational and testing purposes.

    """

    def __init__(self, scope: core.Construct, id: str, *, prefix: str, environment: str, configuration, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.prefix = prefix
        self.environment_ = environment
        validate_configuration(configuration_schema=IOT_ANALYTICS_FAN_IN, configuration_received=configuration)

        # Defining Datastore
        datastore_name = self.prefix + "_" + configuration["datastore_name"] + "_datastore_" + self.environment_
        self._datastore = analytics.CfnDatastore(self, id=datastore_name, datastore_name=datastore_name)

        self._channel_pipes = list()
        for channel_pipe in configuration["channel_pipe_definition"]:
            extra_activities = channel_pipe["extra_activities"]
            base_name = channel_pipe["name"]

            # Defining Channel
            channel_name = self.prefix + "_" + base_name + "_channel_" + self.environment_
            channel = analytics.CfnChannel(self, id=channel_name, channel_name=channel_name)

            # Defining Pipeline Properties
            pipeline_activities = list()

            # Defining Channel Activity Property
            channel_activity_property = analytics.CfnPipeline.ChannelProperty(
                channel_name=channel.channel_name, name=channel.channel_name, next=self._datastore.datastore_name
            )
            pipeline_channel_activity = analytics.CfnPipeline.ActivityProperty(channel=channel_activity_property)
            pipeline_activities.append(pipeline_channel_activity)

            # Defining Datastore Activity Property
            datastore_activity_property = analytics.CfnPipeline.DatastoreProperty(
                datastore_name=self._datastore.datastore_name, name=self._datastore.datastore_name
            )
            pipeline_datastore_activity = analytics.CfnPipeline.ActivityProperty(datastore=datastore_activity_property)
            pipeline_activities.append(pipeline_datastore_activity)

            # Appending extra Pipeline Activities
            pipeline_activities.extend(extra_activities)

            # Defining Pipeline
            pipeline_name = self.prefix + "_" + base_name + "_pipeline_" + self.environment_
            pipeline = analytics.CfnPipeline(
                self, id=pipeline_name, pipeline_name=pipeline_name, pipeline_activities=pipeline_activities
            )
            pipeline.add_depends_on(target=self._datastore)
            pipeline.add_depends_on(target=channel)

            self._channel_pipes.append(dict(channel=channel, pipeline=pipeline))

    @property
    def datastore(self):
        return self._datastore

    @property
    def channel_pipes(self):
        return self._channel_pipes
