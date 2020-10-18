SAGEMAKER_POLICY = {
    "ecr_actions": [
        "ecr:BatchDeleteImage",
        "ecr:BatchGetImage",
        "ecr:CompleteLayerUpload",
        "ecr:CreateRepository",
        "ecr:DescribeRepositories",
        "ecr:GetAuthorizationToken",
        "ecr:InitiateLayerUpload",
        "ecr:PutImage",
        "ecr:UploadLayerPart",
    ],
    "ecr_resources": ["*"],
    "s3_actions": ["s3:GetObject"],
    "s3_resources": ["arn:aws:s3:::iotanalytics-notebook-containers/*"],
}
