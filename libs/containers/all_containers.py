import typing as t
from time import time

from config import DOCKER_USER_SCRIPTS_DIR, DOCKER_COMPILED_FILES_DIR
from libs.containers._base_containers import InterpretedContainer, CompiledContainer
from libs.containers.types import Filename, ExecutableCommand, CodeExecutionCommandOptions


class PythonContainer(InterpretedContainer):
    def __init__(self, time_limit: int, memory_limit: str):
        super().__init__(time_limit, memory_limit)

    @property
    def _docker_image(self) -> str:
        return 'python:3.8-alpine'

    def _build_code_execution_command(self, filename: Filename) -> ExecutableCommand:
        return f'python {DOCKER_USER_SCRIPTS_DIR}/{filename}'


class PyPyContainer(InterpretedContainer):
    def __init__(self, time_limit: int, memory_limit: str):
        super().__init__(time_limit, memory_limit)

    @property
    def _docker_image(self) -> str:
        return 'frolvlad/alpine-pypy'

    def _build_code_execution_command(self, filename: Filename) -> ExecutableCommand:
        return f'pypy3 {DOCKER_USER_SCRIPTS_DIR}/{filename}'


class CppContainer(CompiledContainer):
    def __init__(self, time_limit: int, memory_limit: str):
        super().__init__(time_limit, memory_limit)

    @property
    def _docker_image(self) -> str:
        return 'frolvlad/alpine-gxx'

    def _build_code_compilation_command(self, filename: Filename) -> t.Tuple[ExecutableCommand, Filename]:
        file, _ = filename.split('.')

        compiled_file = f'{file}_compiled'
        command = f'g++ {DOCKER_USER_SCRIPTS_DIR}/{filename} -o {DOCKER_COMPILED_FILES_DIR}/{compiled_file}'
        return command, compiled_file

    def _build_code_execution_command(self, filename: Filename) -> ExecutableCommand:
        return f'{DOCKER_COMPILED_FILES_DIR}/{filename}'


class PascalABCContainer(CompiledContainer):
    def __init__(self, time_limit: int, memory_limit: str):
        super().__init__(time_limit, memory_limit)

    @property
    def _docker_image(self) -> str:
        return 'frolvlad/alpine-fpc:latest'

    def _build_code_compilation_command(self, filename: Filename) -> t.Tuple[ExecutableCommand, Filename]:
        name, _ = filename.split('.')
        compiled_filename = f'{name}_compiled'
        command = f'fpc -o../{DOCKER_COMPILED_FILES_DIR}/{compiled_filename} {DOCKER_USER_SCRIPTS_DIR}/{filename}'
        return command, compiled_filename

    def _build_code_execution_command(self, filename: Filename) -> ExecutableCommand:
        return f'{DOCKER_COMPILED_FILES_DIR}/{filename}'


if __name__ == '__main__':
    with PythonContainer(time_limit=2, memory_limit='128m') as container:
        execution_options = CodeExecutionCommandOptions(filename='python_script.py', stdin=r'3\n4\n5')
        result = container.execute(options=execution_options)
        print(result)

    with PascalABCContainer(time_limit=2, memory_limit='256m') as container:
        execution_options = CodeExecutionCommandOptions(filename='pascal_script.pas', stdin=r'2 3')
        result = container.execute(options=execution_options)
        print(result)
