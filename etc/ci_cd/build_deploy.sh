#!/bin/bash

python setup.py sdist > /dev/null

cat << _EOF_
<!-- index.html -->

<html>
  <body>
    <a href="multa-cdk-recipies-${VERSION}.tar.gz">
      multa-cdk-recipies-${VERSION}.tar.gz
    </a>
  </body>
</html>
_EOF_

aws s3 cp index.html s3://cdkrecipies/multa-cdk-recipies/ > /dev/null
aws s3 cp ./dist/multa-cdk-recipies-${VERSION}.tar.gz s3://cdkrecipies/multa-cdk-recipies/ > /dev/null

rm -rf ./dist/*
