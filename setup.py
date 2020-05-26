import os
import setuptools


VERSION = os.environ.get("VERSION", "0.4.0")
CDK_VERSION = os.environ.get("CDK_VERSION", "1.41.0")

with open("./README.md") as fp:
    long_description = fp.read()

with open("./etc/pip/requirements.txt") as reqs:
    requirements = reqs.read().split("\n")
    del requirements[-1]


setuptools.setup(
    name="multacdkrecipies",
    version=VERSION,
    author="Eugenio Efrain Breijo",
    author_email="eebf1993@gmail.com",
    description="A CDK Python Construct for AWS IoT Infrastructure",
    keywords=["aws", "aws-cdk", "cdk", "infrastructure", "cloudformation", "python", "constructs", "framework"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    maintainer="Eugenio Efrain Breijo",
    maintainer_email="eebf1993@gmail.com",
    url="https://github.com/u93/multacdkrecipies",
    packages=[
        "multacdkrecipies",
        "multacdkrecipies.utils",
        "multacdkrecipies.settings",
        "multacdkrecipies.common",
        "multacdkrecipies.scripts",
        "multacdkrecipies.scripts.iot_analytics_notebook",
    ],
    install_requires=requirements,
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: MacOS X",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Libraries :: Application Frameworks" "Topic :: Utilities",
        "Typing :: Typed",
    ],
)
