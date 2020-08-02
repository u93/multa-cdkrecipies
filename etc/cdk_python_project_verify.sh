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
check_command "1/6 - NPM is not installed, please install it to continue with the setup..."

echo "Updating NPM"
npm install -g npm >> $LOG_DIRECTORY
check_command "2/6 - NPM Update was not successful, please check before re-running..."

echo "Installing/Updating AWS CDK"
npm install -g aws-cdk >> $LOG_DIRECTORY
check_command "3/6 - AWS CDK INSTALL/UPDATE was not successful, please check before re-running..."

echo "Checking if PIP is installed"
pip -V > $PWD/output.tmp >> $LOG_DIRECTORY
check_command "4/6 - PIP is not installed, please install it to continue with the setup..."

echo "Updating Python dependencies"
pip install --upgrade aws-cdk.core >> $LOG_DIRECTORY
check_command "5/6 - AWS CDK INSTALL/UPDATE of Python dependecies was not successful, please check before re-running..."

echo "Installing Python requirements"
pip install -r ./etc/requirements.txt
check_command "6/6 - PIP INSTALL of main Python requiremetns was not successful, please check before re-running..."