from aws_cdk import (
    core,
    aws_iotanalytics as analytics,
)

from .utils import IOT_ANALYTICS_FAN_OUT_SCHEMA, validate_configuration


class AwsIotAnalyticsFanOut(core.Construct):
    """
    AWS CDK Construct that defines an AWS Analytics Pipeline with a Fan-Out approach where one channel ingests all the
    information and distributes over several Pipelines that each one is attach to a Datastore.
    """

    def __init__(self, scope: core.Construct, id: str, *, prefix: str, environment: str, configuration, **kwargs):
        """
        :param scope: Stack class, used by CDK.
        :param id: ID of the construct, used by CDK.
        :param prefix: Prefix of the construct, used for naming purposes.
        :param environment: Environment of the construct, used for naming purposes.
        :param configuration: Configuration of the construct. In this case IOT_ANALYTICS_FAN_OUT.
        :param kwargs: Other parameters that could be used by the construct.
        """
        super().__init__(scope, id, **kwargs)
        self.prefix = prefix
        self.environment_ = environment
        self._configuration = configuration

        # Validating that the payload passed is correct
        validate_configuration(configuration_schema=IOT_ANALYTICS_FAN_OUT_SCHEMA, configuration_received=self._configuration)

        # Defining Channel
        channel_name = self.prefix + "_" + self._configuration["channel_name"] + "_channel_" + self.environment_
        self._channel = analytics.CfnChannel(self, id=channel_name, channel_name=channel_name)

        self._datastore_pipes = list()
        for datastore_pipe in self._configuration["datastore_pipe_definition"]:
            extra_activities = datastore_pipe["extra_activities"]
            base_name = datastore_pipe["name"]

            # Defining Datastore
            datastore_name = self.prefix + "_" + base_name + "_datastore_" + self.environment_
            datastore = analytics.CfnDatastore(self, id=datastore_name, datastore_name=datastore_name)

            # Defining Pipeline Properties
            pipeline_activities = list()

            # Defining Channel Activity Property
            channel_activity_property = analytics.CfnPipeline.ChannelProperty(
                channel_name=self._channel.channel_name, name=self._channel.channel_name, next=datastore.datastore_name,
            )
            pipeline_channel_activity = analytics.CfnPipeline.ActivityProperty(channel=channel_activity_property)
            pipeline_activities.append(pipeline_channel_activity)

            # Defining Datastore Activity Property
            datastore_activity_property = analytics.CfnPipeline.DatastoreProperty(
                datastore_name=datastore.datastore_name, name=datastore.datastore_name
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
            pipeline.add_depends_on(target=datastore)
            pipeline.add_depends_on(target=self._channel)

            self._datastore_pipes.append(dict(datastore=datastore, pipeline=pipeline))

    @property
    def configuration(self):
        """
        :return: Construct configuration.
        """
        return self._configuration

    @property
    def channel(self):
        """
        :return: Construct IoT Analytics Channel.
        """
        return self._channel

    @property
    def datastore_pipes(self):
        """
        :return: List of elements where each one is a dictionary that contains Datastores and Pipelines.
        """
        return self._datastore_pipes
