from aws_cdk import core
from .common import base_bucket
from .utils import S3_BUCKETS_CLUSTER_SCHEMA, validate_configuration


from aws_cdk import (
    core,
    aws_cloudfront as cf,
    aws_codebuild as cb,
    aws_codepipeline as cp,
    aws_codepipeline_actions as cp_actions,
)
from .common import base_bucket
from .utils import S3_SPA_PIPELINE_HOSTING_SCHEMA, validate_configuration


class AwsS3SinglePageAppHostingPipeline(core.Construct):
    """
    """

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
        validate_configuration(configuration_schema=S3_SPA_PIPELINE_HOSTING_SCHEMA, configuration_received=self._configuration)

        self._deployment_bucket = base_bucket(self, **self._configuration["hosting"]["bucket"])

        artifact_bucket_config = {
            "bucket_name": f"{self._configuration['hosting']['bucket']['bucket_name']}-artifacts",
            "versioned": True,
            "public_read_access": False
        }
        self._deployment_artifact_bucket = base_bucket(self, **artifact_bucket_config)

        behaviour = cf.Behavior(
            is_default_behavior=self._configuration["hosting"]["cloudfront_distribution"]["origin_config"]["behaviours"]["is_default_behavior"]
        )
        cloudfront_origins = cf.SourceConfiguration(
            behaviors=[behaviour],
            s3_origin_source=cf.S3OriginConfig(s3_bucket_source=self._deployment_bucket)
        )
        self._cloudfront_distribution = cf.CloudFrontWebDistribution(
            self,
            id=self._configuration["hosting"]["cloudfront_distribution"]["name"],
            origin_configs=[cloudfront_origins]
        )

        self._codebuild_project = cb.Project(
            self,
            id=f"{self._configuration['pipeline']['stages']['build']['name']}-cbproject",
            project_name=f"{self._configuration['pipeline']['stages']['build']['name']}-cbproject",
            build_spec=cb.BuildSpec.from_object(
                {
                    "version": self._configuration["pipeline"]["stages"]["build"].get("version", "0.2"),
                    "phases": {
                        "build": {
                            "commands": self._configuration["pipeline"]["stages"]["build"]["commands"]
                        }
                    },
                    "artifacts": {
                        "base-directory": self._configuration["pipeline"]["stages"]["build"]["build_directory"],
                        "files": self._configuration["pipeline"]["stages"]["build"].get("files", "**/*")
                    }
                }
            )
        )

        source_artifact = cp.Artifact(artifact_name="source_artifact")
        single_page_app_artifact = cp.Artifact(artifact_name="single_page_app_artifact")

        self._s3_single_page_app_pipeline = cp.Pipeline(
            self,
            id=self._configuration["pipeline"]["name"],
            artifact_bucket=self._deployment_artifact_bucket,
            pipeline_name=self._configuration["pipeline"]["name"],
        )

        self._s3_single_page_app_pipeline.add_stage(
            stage_name=self._configuration["pipeline"]["stages"]["github_source"]["name"],
            actions=[
                cp_actions.GitHubSourceAction(
                    action_name=self._configuration["pipeline"]["stages"]["github_source"]["name"],
                    repo=self._configuration["pipeline"]["stages"]["github_source"]["repo"],
                    owner=self._configuration["pipeline"]["stages"]["github_source"]["owner"],
                    oauth_token=core.SecretValue.secrets_manager(
                        secret_id=self._configuration["pipeline"]["stages"]["github_source"]["oauth_token_secret_arn"],
                    ),
                    output=source_artifact
                )
            ]
        )

        self._s3_single_page_app_pipeline.add_stage(
            stage_name=self._configuration["pipeline"]["stages"]["build"]["name"],
            actions=[
                cp_actions.CodeBuildAction(
                    action_name=self._configuration["pipeline"]["stages"]["build"]["name"],
                    input=source_artifact,
                    project=self._codebuild_project,
                    outputs=[single_page_app_artifact]
                )
            ]
        )

        self._s3_single_page_app_pipeline.add_stage(
            stage_name=self._configuration["pipeline"]["stages"]["deploy"]["name"],
            actions=[
                cp_actions.S3DeployAction(
                    action_name=self._configuration["pipeline"]["stages"]["deploy"]["name"],
                    bucket=self._deployment_bucket,
                    input=single_page_app_artifact,
                )
            ]
        )

    @property
    def deployment_bucket(self):
        """
        :return: Deployment bucket for the SPA.
        """
        return self._deployment_bucket

    @property
    def cloudfront_distribution(self):
        """
        :return: Cloudfront Distribution for the SPA deployment bucket.
        """
        return self._cloudfront_distribution

    @property
    def codebuild_project(self):
        """
        :return: CodeBuild Project.
        """
        return self._codebuild_project

    @property
    def s3_single_page_app_pipeline(self):
        """
        :return: Project Pipeline.
        """
        return self._s3_single_page_app_pipeline




