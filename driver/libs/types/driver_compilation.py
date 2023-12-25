from dataclasses import dataclass

from docker.models.containers import ExecResult

from .driver_base import Filename

@dataclass(frozen=True)
class CompiledFileData:
    filename: Filename
    compilation_result: ExecResult
