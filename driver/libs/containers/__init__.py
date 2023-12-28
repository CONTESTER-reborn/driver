import typing as t

from driver.libs.containers._base_containers import _BaseContainer
from driver.libs.containers.all_containers import CppContainer, PascalABCContainer, PyPyContainer, PythonContainer
from driver.libs.enums import ProgrammingLanguage

ContainerClass: t.TypeAlias = t.Type[_BaseContainer]


class ContainersFactory:
    @staticmethod
    def get(language: ProgrammingLanguage) -> ContainerClass:
        containers_mapping: t.Mapping[ProgrammingLanguage, ContainerClass] = {
            ProgrammingLanguage.PYTHON: PythonContainer,
            ProgrammingLanguage.PYPY: PyPyContainer,
            ProgrammingLanguage.CPP: CppContainer,
            ProgrammingLanguage.PASCAL_ABC: PascalABCContainer
        }

        class_ = containers_mapping.get(language, None)
        if class_ is None:
            raise ValueError(f'Language {language} is not specified in mapping!')
        return class_
