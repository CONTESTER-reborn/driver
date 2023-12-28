from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
LOCAL_USER_SCRIPTS_DIR = ROOT_DIR / 'tmp'
DOCKER_USER_SCRIPTS_DIR = 'user-scripts-dir'
DOCKER_COMPILED_FILES_DIR = 'compiled-scripts-dir'
DOCKER_TIME_OUTPUT_FILE = 'time-stdout-file'
