from aws_cdk import (
    core,
    aws_iotanalytics as analytics,
)

from .common import (
    base_iot_rule,
    base_iot_analytics_role,
    base_iot_analytics_channel,
    base_iot_analytics_datastore,
    base_iot_analytics_pipeline,
)
from .utils import IOT_ANALYTICS_FAN_IN_SCHEMA, validate_configuration


class AwsIotAnalyticsFanIn(core.Construct):
    """
    AWS CDK Construct that defines an AWS Analytics Pipeline with a Fan-In approach where multiple channels
    ingests all the information and distributes over several Pipelines that are all attached to a common Datastore.
    """

    def __init__(self, scope: core.Construct, id: str, *, prefix: str, environment: str, configuration, **kwargs):
        """
        :param scope: Stack class, used by CDK.
        :param id: ID of the construct, used by CDK.
        :param prefix: Prefix of the construct, used for naming purposes.
        :param environment: Environment of the construct, used for naming purposes.
        :param configuration: Configuration of the construct. In this case IOT_ANALYTICS_FAN_IN.
        :param kwargs: Other parameters that could be used by the construct.
        """
        super().__init__(scope, id, **kwargs)
        self.prefix = prefix
        self.environment_ = environment
        self._configuration = configuration

        # Validating that the payload passed is correct
        validate_configuration(configuration_schema=IOT_ANALYTICS_FAN_IN_SCHEMA, configuration_received=configuration)

        # Defining Datastore
        datastore_name = self.prefix + "_" + self._configuration["datastore_name"] + "_datastore_" + self.environment_
        self._datastore = analytics.CfnDatastore(self, id=datastore_name, datastore_name=datastore_name)

        self._channel_pipes = list()
        for channel_pipe in self._configuration["channel_pipe_definition"]:
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
            pipeline = analytics.CfnPipeline(self, id=pipeline_name, pipeline_name=pipeline_name, pipeline_activities=pipeline_activities)
            pipeline.add_depends_on(target=self._datastore)
            pipeline.add_depends_on(target=channel)

            self._channel_pipes.append(dict(channel=channel, pipeline=pipeline))

    @property
    def configuration(self):
        """
        :return: Construct configuration.
        """
        return self._configuration

    @property
    def datastore(self):
        """
        :return: Construct IoT Analytics Datastore.
        """
        return self._datastore

    @property
    def channel_pipes(self):
        """
        :return: List of elements where each one is a dictionary that contains Channels and Pipelines.
        """
        return self._channel_pipes
