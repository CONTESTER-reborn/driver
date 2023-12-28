import typing as t

from driver.config import DOCKER_USER_SCRIPTS_DIR, DOCKER_COMPILED_FILES_DIR
from driver.libs.containers._base_containers import InterpretedContainer, CompiledContainer
from driver.libs.files.utils import get_compiled_filename
from driver.libs.types import Filename, ExecutableCommand, CodeExecutionCommandOptions


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
        compiled_filename = get_compiled_filename(filename)
        command = f'g++ {DOCKER_USER_SCRIPTS_DIR}/{filename} -o {DOCKER_COMPILED_FILES_DIR}/{compiled_filename}'
        return command, compiled_filename

    def _build_code_execution_command(self, filename: Filename) -> ExecutableCommand:
        return f'{DOCKER_COMPILED_FILES_DIR}/{filename}'


class PascalABCContainer(CompiledContainer):
    def __init__(self, time_limit: int, memory_limit: str):
        super().__init__(time_limit, memory_limit)

    @property
    def _docker_image(self) -> str:
        return 'frolvlad/alpine-fpc:latest'

    def _build_code_compilation_command(self, filename: Filename) -> t.Tuple[ExecutableCommand, Filename]:
        compiled_filename = get_compiled_filename(filename)
        command = f'fpc -o./{DOCKER_COMPILED_FILES_DIR}/{compiled_filename} {DOCKER_USER_SCRIPTS_DIR}/{filename}'
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
