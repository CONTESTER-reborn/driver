import typing as t
import os
import uuid

from driver.libs.enums import ProgrammingLanguages
from driver.libs.types import Filename
from config import LOCAL_USER_SCRIPTS_DIR

ProgrammingLanguagesMember = t.TypeVar('ProgrammingLanguagesMember', bound=ProgrammingLanguages)


class FileCreator:
    def __enter__(self, source_code: str, programming_language: ProgrammingLanguagesMember):
        # Generating unique name of the file
        name = str(uuid.uuid4())
        extension = programming_language
        self.filename = f'{name}.{extension}'

        # Building path to file
        self.__file_path = LOCAL_USER_SCRIPTS_DIR / self.filename

        # Writing passed source code to the file
        with open(self.__file_path, 'w') as file:
            file.write(source_code)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.remove(self.__file_path)
