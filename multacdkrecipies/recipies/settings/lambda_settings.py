import os

DEFAULT_LAMBDA_CODE_PATH = "./code"

if os.path.isdir(DEFAULT_LAMBDA_CODE_PATH) is True:
    DEFAULT_LAMBDA_CODE_PATH_EXISTS = True
else:
    DEFAULT_LAMBDA_CODE_PATH_EXISTS = False
