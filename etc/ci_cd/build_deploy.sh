#!/bin/bash

S3_BUCKET="cdkrecipies"
PACKAGE_NAME="multacdkrecipies"

ACTION=${1}
export VERSION=${2}

black -t py37 -l 130 ./${S3_BUCKET_FOLDER} > /dev/null
python setup.py sdist > /dev/null

if [ "${ACTION}" == "DEVELOPMENT" ]; then
  cat << _EOF_
<!-- index.html -->

<html>
  <body>
    <a href="${PACKAGE_NAME}-${VERSION}.tar.gz">
      ${PACKAGE_NAME}-${VERSION}.tar.gz
    </a>
  </body>
</html>
_EOF_

  aws s3 cp index.html s3://${S3_BUCKET}/${PACKAGE_NAME}/ > /dev/null
  aws s3 cp ./dist/${PACKAGE_NAME}-${VERSION}.tar.gz s3://${S3_BUCKET}/${PACKAGE_NAME}/ > /dev/null

  rm -rf dist/*

elif [ "${ACTION}" == "PRODUCION" ]; then

  echo "Entering in PRODUCION deployment!"

else

  echo "Wrong input for build/deploy script"

fi
