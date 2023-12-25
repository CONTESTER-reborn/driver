from enum import Enum
from .types import ProgrammingLanguageData, DriverErrorData


class ProgrammingLanguages(Enum):
    PYTHON = ProgrammingLanguageData('Python 3.8', file_extension='py')
    PYPY = ProgrammingLanguageData('PyPy 7.3.12', file_extension='py')
    CPP = ProgrammingLanguageData('GCC Latest', file_extension='cpp')
    PASCAL_ABC = ProgrammingLanguageData('Free Pascal 3.2.2', file_extension='pas')


class DriverErrors(Enum):
    TIME_LIMIT_EXCEEDED = DriverErrorData('Time Limit Exceeded', show_output=False)
    MEMORY_LIMIT_EXCEEDED = DriverErrorData('Memory Limit Exceeded', show_output=False)
    COMPILATION_ERROR = DriverErrorData('Compilation Error', show_output=True)
    RUNTIME_ERROR = DriverErrorData('Run-Time Error', show_output=True)
    UNKNOWN_ERROR: DriverErrorData = DriverErrorData('Unknown Error', show_output=False)
