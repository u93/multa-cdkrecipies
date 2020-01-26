#!/bin/bash

python setup.py sdist > /dev/null

cat << _EOF_
<!-- index.html -->

<html>
  <body>
    <a href="multacdkrecipies-0.0.1.tar.gz">
      multacdkrecipies-0.0.1.tar.gz
    </a>
    <a href="multacdkrecipies-0.0.2.tar.gz">
      multacdkrecipies-0.0.2.tar.gz
    </a>
    <a href="multacdkrecipies-0.0.3.tar.gz">
      multacdkrecipies-0.0.3.tar.gz
    </a>
    <a href="multacdkrecipies-0.0.4.tar.gz">
      multacdkrecipies-0.0.4.tar.gz
    </a>
    <a href="multacdkrecipies-0.0.5.tar.gz">
      multacdkrecipies-0.0.5.tar.gz
    </a>
    <a href="multacdkrecipies-0.0.6.tar.gz">
      multacdkrecipies-0.0.6.tar.gz
    </a>
    <a href="multacdkrecipies-0.0.7.tar.gz">
      multacdkrecipies-0.0.7.tar.gz
    </a>
  </body>
</html>
_EOF_

aws s3 cp index.html s3://cdkrecipies/multacdkrecipies/ > /dev/null
aws s3 cp ./dist/multacdkrecipies-0.0.7.tar.gz s3://cdkrecipies/multacdkrecipies/ > /dev/null
