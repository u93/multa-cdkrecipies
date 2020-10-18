from aws_cdk import core

from multacdkrecipies.common import (
    base_iot_analytics_channel,
    base_iot_analytics_dataset,
    base_iot_analytics_datastore,
    base_iot_analytics_pipeline,
)
from multacdkrecipies.recipies.utils import IOT_ANALYTICS_DATA_WORKFLOW_SCHEMA, validate_configuration


class AwsIotAnalyticsDataWorkflow(core.Construct):
    """
    AWS CDK Construct that defines an AWS Analytics Pipeline with simple Data Flow approach where one channel
    ingests all the information and distributes over a Pipeline that is attached to a common Datastore.
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
        validate_configuration(
            configuration_schema=IOT_ANALYTICS_DATA_WORKFLOW_SCHEMA, configuration_received=self._configuration
        )

        base_name = self._configuration["name"]
        datastore_name = self.prefix + "_" + base_name + "_datastore_" + self.environment_
        channel_name = self.prefix + "_" + base_name + "_channel_" + self.environment_
        pipeline_name = self.prefix + "_" + base_name + "_pipeline_" + self.environment_

        retention_periods = self._configuration.get("retention_periods", dict())

        # Defining Datastore
        datastore_retention_period = retention_periods.get("datastore")
        self._datastore = base_iot_analytics_datastore(
            construct=self, datastore_name=datastore_name, retention_period=datastore_retention_period
        )

        # Defining Channel
        channel_retention_period = retention_periods.get("channel")
        self._channel = base_iot_analytics_channel(
            construct=self, channel_name=channel_name, retention_period=channel_retention_period
        )

        # Defining Pipeline Properties
        activities_dict = dict(channel=self._channel, datastore=self._datastore)
        resources_dependencies = [self._channel, self._datastore]

        # Defining Pipeline
        self._pipeline = base_iot_analytics_pipeline(
            construct=self,
            activities=activities_dict,
            resource_dependencies=resources_dependencies,
            pipeline_name=pipeline_name,
        )

        # Defining Datasets
        self._datasets = list()
        for dataset_configuration in self._configuration.get("datasets", []):
            dataset = base_iot_analytics_dataset(
                construct=self, resource_dependencies=resources_dependencies, **dataset_configuration
            )
            self._datasets.append(dataset)

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
