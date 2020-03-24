from copy import deepcopy

from aws_cdk import (
    core,
    aws_lambda_event_sources as lambda_sources,
)
from .common import base_alarm, base_lambda_function, base_queue
from .utils import SQS_CONFIG_SCHEMA, validate_configuration


class AwsSqsPipes(core.Construct):
    """
    AWS CDK Construct that defines a pipe where a Rules captures an MQTT Message sent to or from AWS IoT MQTT Broker,
    then the message is sent to an SQS Queue and a Lambda function subscribed to the topic can process it and take
    proper actions. The construct takes a few inputs.

    Attributes:
        prefix (str): The prefix set on the name of each resource created in the stack. Just for organization purposes.
        environment_ (str): The environment that all resources will use. Also for organizational and testing purposes.
        _sqs_queue (object): SQS Queue representation in CDK.
        _lambda_function (object): Lambda Function representation in CDK.
        _iot_rule (object): IoT Topic Rule representation in CDK.

    """

    def __init__(self, scope: core.Construct, id: str, *, prefix: str, environment: str, configuration, **kwargs):
        """

        :param scope:
        :param id:
        :param prefix:
        :param environment:
        :param configuration:
        :param kwargs:
        """
        super().__init__(scope, id, **kwargs)
        self.prefix = prefix
        self.environment_ = environment
        self._configuration = configuration

        # Validating that the payload passed is correct
        validate_configuration(configuration_schema=SQS_CONFIG_SCHEMA, configuration_received=self._configuration)

        # Defining SQS Queue
        queue_data = deepcopy(self._configuration["queue"])
        self._sqs_queue = base_queue(construct=self, **queue_data)

        # Validating Lambda Function Runtime
        functions_data = self._configuration["lambda_handlers"]
        self._lambda_functions = list()
        for lambda_function in functions_data:
            _lambda_function = base_lambda_function(self, **lambda_function)
            self._lambda_functions.append(_lambda_function)

            _lambda_function.add_event_source(lambda_sources.SqsEventSource(queue=self._sqs_queue, batch_size=10))

    def set_alarms(self):
        """

        :return:
        """
        if isinstance(self._configuration["queue"].get("alarms"), list) is True:
            sqs_alarms = list()
            for alarm_definition in self._configuration["queue"].get("alarms"):
                sqs_alarms.append(
                    base_alarm(
                        self, resource_name=self._configuration["queue"]["queue_name"], base_resource=self._sqs_queue, **alarm_definition
                    )
                )

        for lambda_function_data, lambda_function_definition in zip(self._configuration["lambda_handlers"], self._lambda_functions):
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
        return self._configuration

    @property
    def sqs_queue(self):
        return self._sqs_queue

    @property
    def lambda_functions(self):
        return self._lambda_functions
