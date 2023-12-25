from dataclasses import dataclass


@dataclass(frozen=True)
class ProgrammingLanguageData:
    full_name: str
    file_extension: str
