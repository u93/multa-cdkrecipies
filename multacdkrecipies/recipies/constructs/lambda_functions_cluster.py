from aws_cdk import core
from multacdkrecipies.common import base_alarm, base_lambda_function
from multacdkrecipies.recipies.utils import LAMBDA_FUNCTIONS_CLUSTER_SCHEMA, validate_configuration


class AwsLambdaFunctionsCluster(core.Construct):
    """"""

    def __init__(self, scope: core.Construct, id: str, *, prefix: str, environment: str, configuration, **kwargs):
        """
        :param scope: Stack class, used by CDK.
        :param id: ID of the construct, used by CDK.
        :param prefix: Prefix of the construct, used for naming purposes.
        :param environment: Environment of the construct, used for naming purposes.
        :param configuration: Configuration of the construct. In this case APIGATEWAY_FAN_OUT_SCHEMA.
        :param kwargs: Other parameters that could be used by the construct.
        """
        super().__init__(scope, id, **kwargs)
        self.prefix = prefix
        self.environment_ = environment
        self._configuration = configuration

        # Validating that the payload passed is correct
        validate_configuration(configuration_schema=LAMBDA_FUNCTIONS_CLUSTER_SCHEMA, configuration_received=self._configuration)

        # Define FAN-Out Lambda functions
        self._lambda_functions = list()
        for lambda_function in self._configuration["functions"]:
            _lambda = base_lambda_function(self, **lambda_function)
            self._lambda_functions.append(_lambda)

    def set_alarms(self):
        """
        Function that set alarms for the resources involved in the construct. Except API Gateway resource.
        :return: None
        """
        function_definition_resource = zip(self._configuration["functions"], self._lambda_functions)
        function_definition_resource_list = list(function_definition_resource)
        functions_alarms = list()
        for lambda_function, resource in function_definition_resource_list:
            if isinstance(lambda_function.get("alarms"), list) is True:
                for alarm_definition in lambda_function.get("alarms"):
                    functions_alarms.append(
                        base_alarm(
                            self,
                            resource_name=lambda_function["lambda_name"],
                            base_resource=resource,
                            **alarm_definition,
                        )
                    )

    @property
    def lambda_functions(self):
        """
        :return: Construct Lambda Functions List.
        """
        return self._lambda_functions
