#!/bin/bash

python setup.py sdist > /dev/null

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
