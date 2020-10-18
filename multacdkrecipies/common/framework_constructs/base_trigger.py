import logging
import traceback

from aws_cdk import (
    core as core,
)

import schema


logger = logging.getLogger(__name__)


class BaseTrigger(core.Construct):
    def __init__(self, scope: core.Construct, id_: str, *, prefix: str, environment: str, configuration, **kwargs):
        """
        :param scope: Stack class, used by CDK.
        :param id_: ID of the construct, used by CDK.
        :param prefix: Prefix of the construct, used for naming purposes.
        :param environment: Environment of the construct, used for naming purposes.
        :param configuration: Configuration of the construct. In this case APIGATEWAY_LAMBDA_SIMPLE_WEB_SERVICE_SCHEMA.
        :param kwargs: Other parameters that could be used by the construct.
        """
        super().__init__(scope, id_, **kwargs)
        self._configuration = configuration
        self._environment = environment
        self._is_valid = None
        self._prefix = prefix
        self._schema = None

    def validate(self):
        """
        Validates the configuration passed to CDK Constructs.
        :param configuration_schema: Base Multa Recipe Schema in the project.
        :param configuration_received: Configuration passed by external application.
        """
        try:
            self._schema.validate(self._configuration)
        except schema.SchemaError:
            logger.error("Improper configuration passed to Multa CDK Construct!!!")
            logger.error(traceback.format_exc())
            self._is_valid = False
        else:
            self._is_valid = True

    @property
    def configuration(self):
        return self._configuration

    @property
    def environment(self):
        return self._environment

    @property
    def is_valid(self):
        return self._is_valid

    @property
    def prefix(self):
        return self._prefix

    @property
    def schema(self):
        return self._schema
