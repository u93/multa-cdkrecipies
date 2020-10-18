from aws_cdk import core, aws_events as events, aws_events_targets as targets
from multacdkrecipies.common import base_alarm, base_lambda_function
from multacdkrecipies.recipies.utils import CLOUDWATCH_CONFIG_SCHEMA, validate_configuration


class AwsCloudwatchLambdaPipes(core.Construct):
    """
    AWS CDK Construct that defines a pipe where a message is sent by a Cloudwatch Rule and a Lambda function or functions
    will process it and take proper actions. The construct allows to set alerts on the Lambda Functions.
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
        validate_configuration(configuration_schema=CLOUDWATCH_CONFIG_SCHEMA, configuration_received=self._configuration)
        rule_configuration = self._configuration["cloudwatch_rule"]

        rule_name = self.prefix + "_" + rule_configuration["rule_name"] + "_" + self.environment_
        schedule = events.Schedule.expression(f"cron({rule_configuration['schedule']})")
        self._cloudwatch_event = events.Rule(
            self,
            id=rule_name,
            rule_name=rule_name,
            description=rule_configuration.get("description"),
            enabled=rule_configuration["enabled"],
            schedule=schedule,
        )

        self._lambda_functions = list()
        for function_definition in self._configuration["lambda_handlers"]:
            function_ = base_lambda_function(self, **function_definition)
            self._cloudwatch_event.add_target(targets.LambdaFunction(handler=function_))
            self._lambda_functions.append(function_)

    def set_alarms(self):
        """
        Function that set alarms for the resources involved in the construct. Except the Cloudwatch Event.
        :return: None
        """

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
    def lambda_functions(self):
        """
        :return: Construct Lambda Function.
        """
        return self._lambda_function

    @property
    def cloudwatch_event(self):
        """
        :return: Construct IoT Rule.
        """
        return self._cloudwatch_event
