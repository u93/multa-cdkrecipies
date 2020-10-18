from copy import deepcopy

from aws_cdk import (
    core,
    aws_sns_subscriptions as sns_subs,
)
from multacdkrecipies.common import base_alarm, base_lambda_function, base_topic
from multacdkrecipies.recipies.utils import SNS_CONFIG_SCHEMA, validate_configuration


class AwsSnsPipes(core.Construct):
    """
    AWS CDK Construct that defines a pipe where a message is sent to an SNS Topic and a Lambda function or functions
    subscribed to the topic can process it and take proper actions. The construct allows to set alerts on both resources
    the SNS Topic and the Lambda Functions.
    """

    def __init__(self, scope: core.Construct, id: str, *, prefix: str, environment: str, configuration, **kwargs):
        """
        :param scope: Stack class, used by CDK.
        :param id: ID of the construct, used by CDK.
        :param prefix: Prefix of the construct, used for naming purposes.
        :param environment: Environment of the construct, used for naming purposes.
        :param configuration: Configuration of the construct. In this case SNS_CONFIG_SCHEMA.
        :param kwargs: Other parameters that could be used by the construct.
        """
        super().__init__(scope, id, **kwargs)
        self.prefix = prefix
        self.environment_ = environment
        self._configuration = configuration

        # Validating that the payload passed is correct
        validate_configuration(configuration_schema=SNS_CONFIG_SCHEMA, configuration_received=self._configuration)

        # Defining SNS Topic
        topic_data = deepcopy(self._configuration["topic"])
        self._sns_topic = base_topic(self, **topic_data)

        # Validating Lambda Function Runtime
        functions_data = self._configuration["lambda_handlers"]
        self._lambda_functions = list()
        for lambda_function in functions_data:
            _lambda_function = base_lambda_function(self, **lambda_function)
            self._lambda_functions.append(_lambda_function)

            # Defining the Lambda subscription to the specified SNS Topic in cdk.json file.
            sns_subscription = sns_subs.LambdaSubscription(fn=_lambda_function)
            self._sns_topic.add_subscription(sns_subscription)

    def set_alarms(self):
        """
        Function that set alarms for the resources involved in the construct.
        :return: None
        """
        if isinstance(self._configuration["topic"].get("alarms"), list) is True:
            sns_alarms = list()
            for alarm_definition in self._configuration["topic"].get("alarms"):
                sns_alarms.append(
                    base_alarm(
                        self,
                        resource_name=self._configuration["topic"]["topic_name"],
                        base_resource=self._sns_topic,
                        **alarm_definition,
                    )
                )

        for lambda_function_data, lambda_function_definition in zip(
            self._configuration["lambda_handlers"], self._lambda_functions
        ):
            if isinstance(lambda_function_data.get("alarms"), list) is True:
                lambda_alarms = list()
                for alarm_definition in lambda_function_data.get("alarms"):
                    lambda_alarms.append(
                        base_alarm(
                            self,
                            resource_name=lambda_function_data.get("lambda_name"),
                            base_resource=lambda_function_definition,
                            **alarm_definition,
                        )
                    )

    @property
    def configuration(self):
        """
        :return: Construct configuration.
        """
        return self._configuration

    @property
    def sns_topic(self):
        """
        :return: Construct SNS Topic.
        """
        return self._sns_topic

    @property
    def lambda_functions(self):
        """
        :return: List of Constructs Lambda Functions.
        """
        return self._lambda_functions
