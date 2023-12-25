from docker.models.containers import ExecResult

import typing as t
from dataclasses import dataclass

from libs.containers.enums import DriverErrors


Filename: t.TypeAlias = str
ExecutableCommand: t.TypeAlias = str


@dataclass(frozen=True)
class CodeExecutionCommandOptions:
    filename: Filename
    stdin: str


@dataclass(frozen=True)
class CompiledFileData:
    filename: Filename
    compilation_result: ExecResult


@dataclass(frozen=True)
class DriverErrorType:
    value: DriverErrors
    show_output: bool

@dataclass
class ProcessedExecutionResult:
    exit_code: int
    output: str
    execution_time: float
    error_type: str
