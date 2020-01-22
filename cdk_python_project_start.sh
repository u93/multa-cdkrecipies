#!/bin/bash

LOG_DIRECTORY="$PWD/output.tmp"

check_command() {
  if [ ! $? -eq 0 ]; then
    echo $1
    exit 1
  fi
}

echo "Checking if NPM is installed"
npm -v >> $LOG_DIRECTORY
check_command "1/7 - NPM is not installed, please install it to continue with the setup..."

echo "Updating NPM"
npm install -g npm >> $LOG_DIRECTORY
check_command "2/7 - NPM Update was not successful, please check before re-running..."

echo "Installing/Updating AWS CDK"
npm install -g aws-cdk >> $LOG_DIRECTORY
check_command "3/7 - AWS CDK INSTALL/UPDATE was not successful, please check before re-running..."

echo "Checking if PIP is installed"
pip -V > $PWD/output.tmp >> $LOG_DIRECTORY
check_command "4/7 - PIP is not installed, please install it to continue with the setup..."

echo "Updating Python dependencies"
pip install --upgrade aws-cdk.core >> $LOG_DIRECTORY
check_command "5/7 - AWS CDK INSTALL/UPDATE of Python dependecies was not successful, please check before re-running..."

echo "Initializing CDK project"
mkdir aws-iot-rule-sqs-lambda-pipe && cd aws-iot-rule-sqs-lambda-pipe >> $LOG_DIRECTORY
cdk init --generate-only --language python && mv cdk.json ..
check_command "6/7 - Initializing CDK project failed, please check output before re-running..."

echo "Configuring project structure to escale it"
# mv appcdk mainstack && touch __init__.py >> $LOG_DIRECTORY
# sed -e '5s/.*/from appcdk.mainstack.appcdk_stack import AppcdkStack/' -i '' app.py
chmod +x app.py

echo "Removing unnecessary files"
# rm README.md && rm requirements.txt && rm aws_iot_rules_sns_pipes_setup.py && rm source.bat >> $LOG_DIRECTORY
# check_command "7/7 -Removing action of unnecesary project files failed, please check output before re-running..."

echo "Project setup successfully"
echo "To RUN the project from your project root folder, please execute -> cdk synth --app appcdk/app.py"