from dataclasses import dataclass


@dataclass(frozen=True)
class DriverErrorData:
    # Human readable error message (e.g. "Time Limit Exceeded")
    message: str
    # In case of error, determines whether stdout will be shown (returned)
    show_output: bool
