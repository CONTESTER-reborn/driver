import typing as t

from docker.models.containers import ExecResult as DockerExecResult

from driver.libs.types import ProcessedContainerExecutionResult
from driver.libs.enums import DriverError

_Stream = t.Optional[bytes]


class ResultProcessor:
    def __init__(
            self,
            execution_result: t.Optional[DockerExecResult] = None,
            compilation_result: t.Optional[DockerExecResult] = None
    ):
        """
        :param execution_result: Result of code execution
        :param compilation_result: Result of code compilation
        :raises ValueError: If both `execution_result` and `compilation_result` are None
        """
        self.__execution_result = execution_result
        self.__compilation_result = compilation_result

        if self.__compilation_result is None and self.__execution_result is None:
            raise ValueError('There must be at least one argument that is not None')

        self.EXIT_CODE_TO_ERROR_MAP: t.Mapping[int, DriverError] = {
            1: DriverError.RUNTIME_ERROR,
            9: DriverError.MEMORY_LIMIT_EXCEEDED,
            15: DriverError.TIME_LIMIT_EXCEEDED
        }

    @staticmethod
    def __decode_streams(output: t.Tuple[_Stream, _Stream]) -> t.Tuple[str, str]:
        """Decodes stdout and stderr streams"""
        stdout, stderr = output
        stdout_decoded = stdout.decode('utf-8') if stdout else ''
        stderr_decoded = stderr.decode('utf-8') if stderr else ''

        return stdout_decoded, stderr_decoded

    @staticmethod
    def __process_stdout(stdout: str) -> t.Tuple[str, float]:
        """Separates actual stdout from execution time"""
        split_stdout = stdout.rsplit('\n', 2)

        if len(split_stdout) == 2:
            actual_output = ''
            execution_time, _ = split_stdout
        else:
            actual_output, execution_time, _ = stdout.rsplit('\n', 2)

        return actual_output, float(execution_time)

    def __handle_compilation(self) -> t.Optional[ProcessedContainerExecutionResult]:
        # NOTE! compilation_result.stdout returns both stdout and stderr, since demux flag is set to True
        stdout, stderr = self.__decode_streams(self.__compilation_result.stdout)

        # Checking if compilation failed
        if compilation_result.exit_code != 0:
            return ProcessedContainerExecutionResult(
                exit_code=self.__compilation_result.exit_code,
                output=stderr,
                execution_time=0,
                error_message=DriverError.COMPILATION_ERROR.value.message
            )
        return None

    def __handle_execution(self) -> ProcessedContainerExecutionResult:
        # Retrieving actual stdout and execution time
        # NOTE! execution_result.stdout returns both stdout and stderr, since demux flag is set to True
        stdout, stderr = self.__decode_streams(self.__execution_result.stdout)

        if self.__execution_result.exit_code == 0:
            output, execution_time = self.__process_stdout(stdout)
            error_message = ''
        else:
            # Execution time
            execution_time = 0

            # Error message and output
            error_data = self.EXIT_CODE_TO_ERROR_MAP.get(self.__execution_result.exit_code, DriverError.UNKNOWN_ERROR)
            error_message = error_data.value.message
            # Setting output as value from stderr
            output = stderr
            # If this error implies that stdout must be hidden, setting output as empty string
            if not error_data.value.show_output:
                output = ''

        return ProcessedContainerExecutionResult(
            exit_code=self.__execution_result.exit_code,
            output=output,
            execution_time=execution_time,
            error_message=error_message
        )

    def process(self) -> ProcessedContainerExecutionResult:
        if self.__compilation_result:
            processed_compilation_result = self.__handle_compilation()
            # If we got some kind of result after handling compilation, returning it
            if processed_compilation_result:
                return processed_compilation_result

        return self.__handle_execution()