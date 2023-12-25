from enum import Enum


class DriverErrors(str, Enum):
    TIME_LIMIT_EXCEEDED = 'Time Limit Exceeded'
    MEMORY_LIMIT_EXCEEDED = 'Memory Limit Exceeded'
    COMPILATION_ERROR = 'Compilation Error'
    RUNTIME_ERROR = 'Run-Time Error'
    UNKNOWN_ERROR = 'Unknown Error'
