from glob import glob
import os

try:
    python_lib_dir = glob(f"{os.environ.get('VIRTUAL_ENV')}/lib/*")[0].split("/")[-1]
except Exception:
    python_lib_dir = "python3.7"

DEFAULT_LAMBDA_LAYER_CODE_INSTALL_PATH = f"./etc/layer/python/lib/{python_lib_dir}/site-packages/"
DEFAULT_LAMBDA_LAYER_CODE_PATH = "./etc/layer/"
if os.path.isdir(DEFAULT_LAMBDA_LAYER_CODE_INSTALL_PATH) is True:
    DEFAULT_LAMBDA_LAYER_CODE_PATH_EXISTS = True
else:
    DEFAULT_LAMBDA_LAYER_CODE_PATH_EXISTS = False

DEFAULT_LAMBDA_LAYER_REQUIREMENTS_PATH = f"./etc/pip/lambda-requirements.txt"
if os.path.isfile(DEFAULT_LAMBDA_LAYER_REQUIREMENTS_PATH) is True:
    DEFAULT_LAMBDA_LAYER_REQUIREMENTS_PATH_EXISTS = True
else:
    DEFAULT_LAMBDA_LAYER_REQUIREMENTS_PATH_EXISTS = False
