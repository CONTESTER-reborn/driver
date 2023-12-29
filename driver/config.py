from os import environ
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

# Volume with user scripts
USER_SCRIPTS_VOLUME_PREFIX = 'driver'  # Same as name of service in docker-compose
USER_SCRIPTS_VOLUME_NAME = 'user-scripts-volume'  # Same as name of volume in docker-compose
USER_SCRIPTS_VOLUME_FULLNAME = f'{USER_SCRIPTS_VOLUME_PREFIX}_{USER_SCRIPTS_VOLUME_NAME}'

# Local files and folders
LOCAL_USER_SCRIPTS_DIR = ROOT_DIR / environ.get('LOCAL_USER_SCRIPTS_DIR', 'tmp')

# Files and folders inside each automatically created container
DOCKER_USER_SCRIPTS_DIR = 'user-scripts-local'
DOCKER_COMPILED_FILES_DIR = 'compiled-scripts-local'
DOCKER_TIME_OUTPUT_FILE = 'time-stdout-file'
