import typing as t
import os
import uuid

from driver.libs.containers import _BaseContainer
from driver.libs.enums import ProgrammingLanguage
from driver.libs.types import Filename
from config import LOCAL_USER_SCRIPTS_DIR, DOCKER_USER_SCRIPTS_DIR

ProgrammingLanguagesMember = t.TypeVar('ProgrammingLanguagesMember', bound=ProgrammingLanguage)


class FileCreator:
    def __init__(self, source_code: str, programming_language: ProgrammingLanguage, container: _BaseContainer):
        self.filename: str
        self.__container = container._container
        self.__source_code = self.__escape_quotes(source_code)
        self.__programming_language = programming_language

    def __generate_filename(self) -> Filename:
        name = str(uuid.uuid4())
        extension = self.__programming_language.value.file_extension
        return f'{name}.{extension}'

    def __enter__(self) -> "FileCreator":
        # Generating unique name of the file
        self.filename = self.__generate_filename()

        # Writing passed source code to the file
        file_write_command = f'sh -c \'echo -e \"{self.__source_code}\" > {DOCKER_USER_SCRIPTS_DIR}/{self.filename}\''
        self.__container.exec_run(cmd=file_write_command)
        return self

    @staticmethod
    def __escape_quotes(data: str) -> str:
        replacement_map = {
            '\'': r'\'',
            '\"': r'\"',
        }
        for replace_from, replace_to in replacement_map.items():
            data = data.replace(replace_from, replace_to)
        return data

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__container.exec_run(cmd=f'rm {DOCKER_USER_SCRIPTS_DIR}/{self.filename}')
