from aws_cdk import core

from multacdkrecipies.common import (
    base_iot_analytics_channel,
    base_iot_analytics_dataset,
    base_iot_analytics_datastore,
    base_iot_analytics_pipeline,
)
from multacdkrecipies.recipies.utils import IOT_ANALYTICS_FAN_IN_SCHEMA, validate_configuration


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
        datastore_definition = self._configuration["datastore_definition"]
        datastore_name = self.prefix + "_" + datastore_definition["name"] + "_datastore_" + self.environment_
        datastore_retention_period = datastore_definition["datastore_retention_period"]
        self._datastore = base_iot_analytics_datastore(
            self, datastore_name=datastore_name, retention_period=datastore_retention_period
        )

        self._channel_pipes = list()
        resources_dependencies = list()
        for channel_pipe in self._configuration["channel_pipe_definition"]:
            extra_activities = channel_pipe.get("extra_activities")
            base_name = channel_pipe["name"]
            channel_retention_period = channel_pipe.get("channel_retention_period")

            # Defining Channel
            channel_name = self.prefix + "_" + base_name + "_channel_" + self.environment_
            channel = base_iot_analytics_channel(self, channel_name=channel_name, retention_period=channel_retention_period)

            # Defining Pipeline Properties
            pipeline_name = self.prefix + "_" + base_name + "_pipeline_" + self.environment_
            activities_dict = dict(channel=channel, datastore=self._datastore)

            individual_resource_dependencies = [channel, self._datastore]
            resources_dependencies.extend(individual_resource_dependencies)

            # Defining Channel Activity Property
            pipeline = base_iot_analytics_pipeline(
                self,
                activities=activities_dict,
                resource_dependencies=individual_resource_dependencies,
                pipeline_name=pipeline_name,
            )

            self._channel_pipes.append(dict(channel=channel, pipeline=pipeline))

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
    def channel_pipes(self):
        """
        :return: List of elements where each one is a dictionary that contains Channels and Pipelines.
        """
        return self._channel_pipes
