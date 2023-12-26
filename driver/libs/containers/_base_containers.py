import typing as t
from abc import ABC, abstractmethod

import docker
from docker.models.containers import Container, ExecResult

from config import LOCAL_USER_SCRIPTS_DIR, DOCKER_USER_SCRIPTS_DIR, DOCKER_COMPILED_FILES_DIR, DOCKER_TIME_OUTPUT_FILE
from driver.libs.enums import DriverError
from driver.libs.types import Filename, ExecutableCommand, CodeExecutionCommandOptions
from driver.libs.types import CompiledFileData, ProcessedContainerExecutionResult
from driver.libs.containers.result_processor import ResultProcessor

client = docker.from_env()


class _BaseContainer(ABC):
    """Base class of all containers for programming languages"""

    def __init__(self, time_limit: int, memory_limit: str):
        """
        :param time_limit: Integer message that represents how many seconds can be spent on a single code execution
        :param memory_limit: String with a units identification char (100000b, 1000k, 128m, 1g).
                             If a string is specified without a units character,
                             bytes are assumed as an intended unit
        """
        self.__time_limit = time_limit
        self.__memory_limit = memory_limit

    @property
    @abstractmethod
    def _docker_image(self) -> str:
        """
        Container's property with name of docker image that will be used in order to create a container

        For example: `python:3.8-alpine` or `gcc:latest`
        """
        pass

    @abstractmethod
    def _build_code_execution_command(self, filename: Filename) -> ExecutableCommand:
        """
        Returns command that will execute code

        For instance, if you want to execute python code, then this method should return string like this:
        `python dir/filename.py`
        """
        pass

    def _build_full_code_execution_command(self, options: CodeExecutionCommandOptions) -> ExecutableCommand:
        """
        Wraps result of `_build_code_execution_command` in all other necessary commands
        (such as `time`, `timeout`, adds stdin pipe) via `ExecutionCommandBuilder`
        """
        command = self._build_code_execution_command(options.filename)
        # Aliases
        stdin = options.stdin
        timeout = self.__time_limit
        # Building full command
        command_with_timeout = f'timeout {timeout} {command}'
        command_with_time = f'time -f \"%e\" -o {DOCKER_TIME_OUTPUT_FILE} {command_with_timeout}'
        command_with_time_output = f'{command_with_time} && cat {DOCKER_TIME_OUTPUT_FILE}'
        command_wth_stdin = f'echo -e \"{stdin}\" | {command_with_time_output}'
        full_command = f'sh -c \'{command_wth_stdin}\''

        print(full_command)
        return full_command

    @abstractmethod
    def execute(self, options: CodeExecutionCommandOptions) -> ProcessedContainerExecutionResult:
        """Executes all the commands that are required to get results of passed program"""
        pass

    def __enter__(self):
        # Read-only volume with users' scripts
        scripts_volume = f'{LOCAL_USER_SCRIPTS_DIR}:/{DOCKER_USER_SCRIPTS_DIR}:ro'

        # Creating and starting the container
        self._container: Container = client.containers.create(
            image=self._docker_image,
            volumes=[scripts_volume],
            mem_limit=self.__memory_limit,
            tty=True,
        )

        # Starting the container
        self._container.start()
        # Creating directory for compiled files and file for stdout of `time` command
        self._container.exec_run(f'sh -c \'mkdir {DOCKER_COMPILED_FILES_DIR} && touch {DOCKER_TIME_OUTPUT_FILE}\'')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Stopping and deleting container
        self._container.kill()
        self._container.remove()
        # pass


class InterpretedContainer(_BaseContainer, ABC):
    """Base class of all containers for interpreted programming languages"""

    def __init__(self, time_limit: int, memory_limit: str):
        super().__init__(time_limit, memory_limit)

    def execute(self, options: CodeExecutionCommandOptions) -> ProcessedContainerExecutionResult:
        # Executing
        code_execution_command = self._build_full_code_execution_command(options)
        execution_result = self._container.exec_run(cmd=code_execution_command, stdin=True, demux=True)
        print(execution_result)

        # return execution_result
        result_processor = ResultProcessor()
        return result_processor.handle_execution(execution_result)


class CompiledContainer(_BaseContainer, ABC):
    """Base class of all containers for compiled programming languages"""

    def __init__(self, time_limit: int, memory_limit: str):
        super().__init__(time_limit, memory_limit)
        # Key - original name of file, message name of compiled file
        self.__compiled_files_data: t.Dict[Filename, CompiledFileData] = {}

    @abstractmethod
    def _build_code_compilation_command(self, filename: Filename) -> t.Tuple[ExecutableCommand, Filename]:
        """Returns command that will compile code

        For instance, if you want to compile C++ code, then this method should return string like this:
        `g++ hello.cpp -o hello`
        """
        pass

    def execute(self, options: CodeExecutionCommandOptions) -> ProcessedContainerExecutionResult:
        # Checking if compilation is needed
        if options.filename not in self.__compiled_files_data.keys():
            # Compiling
            code_compilation_command, compiled_filename = self._build_code_compilation_command(options.filename)
            print(code_compilation_command)
            compilation_result = self._container.exec_run(cmd=code_compilation_command)

            # Saving data of compilation to `__compiled_files` hashmap
            data = CompiledFileData(filename=compiled_filename, compilation_result=compilation_result)
            self.__compiled_files_data[options.filename] = data

        # Checking if compilation failed
        compiled_file_data = self.__compiled_files_data[options.filename]
        if compiled_file_data.compilation_result.exit_code != 0:
            # Processing
            result_processor = ResultProcessor(compilation_result=compilation_result)
            return result_processor.handle_compilation(compiled_file_data.compilation_result)

        # Executing
        execution_command_options = CodeExecutionCommandOptions(filename=compiled_filename, stdin=options.stdin)
        code_execution_command = self._build_full_code_execution_command(execution_command_options)
        execution_result = self._container.exec_run(cmd=code_execution_command, stdin=True, demux=True)

        # Processing result
        result_processor = ResultProcessor(execution_result=execution_result, compilation_result=compilation_result)
        return result_processor.handle_execution(execution_result)
