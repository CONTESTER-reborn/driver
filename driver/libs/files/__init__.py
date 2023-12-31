import os
import typing as t
import uuid

from driver.config import LOCAL_USER_SCRIPTS_DIR
from driver.libs.enums import ProgrammingLanguage
from driver.libs.types import Filename

ProgrammingLanguagesMember = t.TypeVar('ProgrammingLanguagesMember', bound=ProgrammingLanguage)


class FileCreator:
    def __init__(self, source_code: str, programming_language: ProgrammingLanguage):
        self.__source_code = source_code
        self.__programming_language = programming_language

    def __generate_filename(self) -> Filename:
        name = str(uuid.uuid4())
        extension = self.__programming_language.value.file_extension
        return f'{name}.{extension}'

    def __enter__(self):
        # Generating unique name of the file
        self.filename = self.__generate_filename()
        # Building path to file
        self.__file_path = LOCAL_USER_SCRIPTS_DIR / self.filename

        # Writing passed source code to the file
        with open(self.__file_path, 'w') as file:
            file.write(self.__source_code)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.remove(self.__file_path)
