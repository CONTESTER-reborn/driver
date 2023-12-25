from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
LOCAL_USER_SCRIPTS_DIR = ROOT_DIR / 'tmp'
DOCKER_USER_SCRIPTS_DIR = 'user-scripts'
DOCKER_COMPILED_FILES_DIR = 'compiled-scripts'