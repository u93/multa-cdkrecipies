#!/bin/bash

ACTION=${1}
export VERSION=${2}

black -t py37 -l 130 ./multacdkrecipies > /dev/null
python setup.py sdist > /dev/null

if [ "${ACTION}" == "DEVELOPMENT" ]; then
  cat << _EOF_
<!-- index.html -->

<html>
  <body>
    <a href="multacdkrecipies-${VERSION}.tar.gz">
      multacdkrecipies-${VERSION}.tar.gz
    </a>
  </body>
</html>
_EOF_

  aws s3 cp index.html s3://cdkrecipies/multacdkrecipies/ > /dev/null
  aws s3 cp ./dist/multacdkrecipies-${VERSION}.tar.gz s3://cdkrecipies/multacdkrecipies/ > /dev/null

  rm -rf dist/*

elif [ "${ACTION}" == "PRODUCION" ]; then

  echo "Entering in PRODUCION deployment!"

else

  echo "Wrong input for build/deploy script"

fi
