import typing as t
from abc import ABC, abstractmethod

import docker
from docker.models.containers import Container, ExecResult

from config import LOCAL_USER_SCRIPTS_DIR, DOCKER_USER_SCRIPTS_DIR, DOCKER_COMPILED_FILES_DIR
from driver.libs.containers.utils import ExecutionCommandBuilder
from driver.libs.enums import DriverErrors
from driver.libs.types import Filename, ExecutableCommand, CodeExecutionCommandOptions
from driver.libs.types import CompiledFileData, ProcessedExecutionResult

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
        execution_command = self._build_code_execution_command(options.filename)
        print(ExecutionCommandBuilder.build(execution_command, options.stdin, self.__time_limit))
        return ExecutionCommandBuilder.build(execution_command, options.stdin, self.__time_limit)

    @staticmethod
    def __process_output(output: str) -> t.Tuple[str, float]:
        """Separates actual output from execution time"""
        actual_output, execution_time, _ = output.rsplit('\n', 2)
        return actual_output, float(execution_time)

    def _process_execution_result(
            self,
            execution_result: t.Optional[ExecResult] = None,
            compilation_result: t.Optional[ExecResult] = None
    ) -> ProcessedExecutionResult:
        """
        Processes compilation and execution results and returns uniform response

        :raises ValueError: If both `execution_result` and `compilation_result` are None
        """

        # Key - exit code, message - `DriverErrorType`
        exit_code_error_map: t.Mapping[int, DriverErrors] = {
            1: DriverErrors.RUNTIME_ERROR,
            9: DriverErrors.MEMORY_LIMIT_EXCEEDED,
            15: DriverErrors.TIME_LIMIT_EXCEEDED
        }

        # Checking if there are any results of compilation
        if compilation_result is not None:
            # Checking if compilation failed
            if compilation_result.exit_code != 0:
                return ProcessedExecutionResult(
                    exit_code=compilation_result.exit_code,
                    output=compilation_result.output.decode('utf-8'),
                    execution_time=0,
                    error_message=DriverErrors.COMPILATION_ERROR.value.message
                )

        # Checking if there are any results of execution
        if execution_result is not None:
            # Retrieving actual output and execution time
            decoded_output = execution_result.output.decode('utf-8')
            actual_output, execution_time = self.__process_output(decoded_output)

            if execution_result.exit_code == 0:
                error_message = ''
            else:
                default_error = DriverErrors.UNKNOWN_ERROR
                error_data = exit_code_error_map.get(execution_result.exit_code, default_error)
                error_message = error_data.value.message

                # If this error implies that output must be hidden, setting output as empty string
                if not error_data.value.show_output:
                    actual_output = ''

            return ProcessedExecutionResult(
                exit_code=execution_result.exit_code,
                output=actual_output,
                execution_time=execution_time,
                error_message=error_message
            )

        raise ValueError('There must be at least one argument that is not None')

    @abstractmethod
    def execute(self, options: CodeExecutionCommandOptions) -> ProcessedExecutionResult:
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
        # Creating directory with name from `DOCKER_COMPILED_FILES_DIR` variable
        self._container.exec_run(f'mkdir {DOCKER_COMPILED_FILES_DIR}')
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

    def execute(self, options: CodeExecutionCommandOptions) -> ProcessedExecutionResult:
        # Executing
        code_execution_command = self._build_full_code_execution_command(options)
        execution_result = self._container.exec_run(cmd=code_execution_command, stdin=True)

        # return execution_result
        return self._process_execution_result(execution_result=execution_result)


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

    def execute(self, options: CodeExecutionCommandOptions) -> ProcessedExecutionResult:
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
            return self._process_execution_result(compilation_result=compilation_result)

        # Executing
        execution_command_options = CodeExecutionCommandOptions(filename=compiled_filename, stdin=options.stdin)
        code_execution_command = self._build_full_code_execution_command(execution_command_options)
        execution_result = self._container.exec_run(cmd=code_execution_command, stdin=True)

        # return execution_result
        return self._process_execution_result(execution_result=execution_result, compilation_result=compilation_result)
