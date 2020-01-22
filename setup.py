import setuptools


with open("./README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="multacdkrecipies",
    version="0.0.1",
    url="http://cdkrecipies.s3-website-us-east-1.amazonaws.com",
    description="A CDK Python Construct for AWS IoT Infrastructure",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Eugenio Efrain Breijo",
    author_email="eebf1993@gmail.com",
    packages=["multacdkrecipies"],
    install_requires=[
        "aws_cdk.core",
        "aws-cdk.aws_iam",
        "aws-cdk.aws_iam",
        "aws-cdk.aws_iot",
        "aws-cdk.aws_lambda",
        "aws-cdk.aws_sns",
        "aws-cdk.aws_sns_subscriptions",
        "schema",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)