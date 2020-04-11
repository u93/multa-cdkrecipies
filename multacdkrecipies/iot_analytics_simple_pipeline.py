from aws_cdk import (
    core,
    aws_iot as iot,
    aws_iotanalytics as analytics,
)

from .common import base_iot_rule, base_iot_analytics_role
from .utils import IOT_ANALYTICS_SIMPLE_PIPELINE, validate_configuration


class AwsIotAnalyticsSimplePipeline(core.Construct):
    """
    AWS CDK Construct that defines an AWS Analytics Simple Pipeline where an IoT Topic Rule routes meesages directly
    to an IoT Analytics Channel of a simple Data Flow approach where one channel ingests all the information and
    distributes over a Pipeline that is attached to a common Datastore.
    """

    def __init__(self, scope: core.Construct, id: str, *, prefix: str, environment: str, configuration, **kwargs):
        """
        :param scope: Stack class, used by CDK.
        :param id: ID of the construct, used by CDK.
        :param prefix: Prefix of the construct, used for naming purposes.
        :param environment: Environment of the construct, used for naming purposes.
        :param configuration: Configuration of the construct. In this case IOT_ANALYTICS_DATA_WORKFLOW.
        :param kwargs: Other parameters that could be used by the construct.
        """
        super().__init__(scope, id, **kwargs)
        self.prefix = prefix
        self.environment_ = environment
        self._configuration = configuration

        # Validating that the payload passed is correct
        validate_configuration(configuration_schema=IOT_ANALYTICS_SIMPLE_PIPELINE, configuration_received=self._configuration)

        base_name = self._configuration["analytics_resource_name"]
        datastore_name = self.prefix + "_" + base_name + "_datastore_" + self.environment_
        channel_name = self.prefix + "_" + base_name + "_channel_" + self.environment_
        pipeline_name = self.prefix + "_" + base_name + "_pipeline_" + self.environment_

        # Defining Datastore
        self._datastore = analytics.CfnDatastore(self, id=datastore_name, datastore_name=datastore_name)

        # Defining Channel
        self._channel = analytics.CfnChannel(self, id=channel_name, channel_name=channel_name)

        # Defining Pipeline Properties
        pipeline_activities = list()

        # Defining Channel Activity Property
        channel_activity_property = analytics.CfnPipeline.ChannelProperty(
            channel_name=self._channel.channel_name, name=self._channel.channel_name, next=self._datastore.datastore_name,
        )
        pipeline_channel_activity = analytics.CfnPipeline.ActivityProperty(channel=channel_activity_property)
        pipeline_activities.append(pipeline_channel_activity)

        # Defining Datastore Activity Property
        datastore_activity_property = analytics.CfnPipeline.DatastoreProperty(
            datastore_name=self._datastore.datastore_name, name=self._datastore.datastore_name
        )
        pipeline_datastore_activity = analytics.CfnPipeline.ActivityProperty(datastore=datastore_activity_property)
        pipeline_activities.append(pipeline_datastore_activity)

        # Defining Pipeline
        self._pipeline = analytics.CfnPipeline(
            self, id=pipeline_name, pipeline_name=pipeline_name, pipeline_activities=pipeline_activities
        )
        self._pipeline.add_depends_on(target=self._datastore)
        self._pipeline.add_depends_on(target=self._channel)

        # Defining IAM Role
        role = base_iot_analytics_role(self, resource_name=self._channel.channel_name, principal_resource="iot")

        # Defining Topic Rule properties
        action = iot.CfnTopicRule.IotAnalyticsActionProperty(channel_name=self._channel.channel_name, role_arn=role.role_arn)
        action_property = iot.CfnTopicRule.ActionProperty(iot_analytics=action)

        rule_data = self._configuration["iot_rule"]
        self._iot_rule = base_iot_rule(self, action_property=action_property, **rule_data)

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
    def channel(self):
        """
        :return: Construct IoT Analytics Channel.
        """
        return self._channel

    @property
    def pipeline(self):
        """
        :return: Construct IoT Analytics Pipeline.
        """
        return self._pipeline

    @property
    def iot_rule(self):
        """
        :return: Construct IoT Topic Rule.
        """
        return self._iot_rule
