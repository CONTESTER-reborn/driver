from dataclasses import dataclass

from .driver_base import Filename


@dataclass(frozen=True)
class CodeExecutionCommandOptions:
    filename: Filename
    stdin: str


@dataclass
class ProcessedContainerExecutionResult:
    exit_code: int
    output: str
    execution_time: float
    error_message: str
