from aws_cdk import core

from multacdkrecipies.common import (
    base_iot_analytics_channel,
    base_iot_analytics_dataset,
    base_iot_analytics_datastore,
    base_iot_analytics_pipeline,
)
from multacdkrecipies.recipies.utils import IOT_ANALYTICS_FAN_OUT_SCHEMA, validate_configuration


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
        channel_data = self._configuration["channel"]
        channel_name = self.prefix + "_" + channel_data["name"] + "_channel_" + self.environment_
        channel_retention_period = channel_data.get("channel_retention_period")
        self._channel = base_iot_analytics_channel(self, channel_name=channel_name, retention_period=channel_retention_period)

        self._datastore_pipes = list()
        resources_dependencies = list()
        for datastore_pipe in self._configuration["datastore_pipe_definition"]:
            extra_activities = datastore_pipe.get("extra_activities")
            base_name = datastore_pipe["name"]

            # Defining Datastore
            datastore_name = self.prefix + "_" + base_name + "_datastore_" + self.environment_
            datastore_retention_period = datastore_pipe.get("datastore_retention_period")
            datastore = base_iot_analytics_datastore(
                self, datastore_name=datastore_name, retention_period=datastore_retention_period
            )

            # Defining Pipeline Properties
            pipeline_name = self.prefix + "_" + base_name + "_pipeline_" + self.environment_
            activities_dict = dict(channel=self._channel, datastore=datastore)
            individual_resources_dependencies = [self._channel, datastore]
            resources_dependencies.extend(individual_resources_dependencies)

            # Defining Pipeline
            pipeline = base_iot_analytics_pipeline(
                self,
                activities=activities_dict,
                resource_dependencies=individual_resources_dependencies,
                pipeline_name=pipeline_name,
            )

            self._datastore_pipes.append(dict(datastore=datastore, pipeline=pipeline))

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
