#!/bin/bash

cd /tmp || exit

aws s3 cp s3://iotanalytics-notebook-containers/iota_notebook_containers.zip ./

unzip iota_notebook_containers.zip

su - ec2-user -c 'source activate JupyterSystemEnv && cd /tmp/iota_notebook_containers && sh install.sh'