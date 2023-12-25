import typing as t

from driver.libs.containers._base_containers import _BaseContainer
from driver.libs.containers.all_containers import PythonContainer, PyPyContainer, CppContainer, PascalABCContainer
from driver.libs.enums import ProgrammingLanguages

ContainerClass: t.TypeAlias = t.Type[_BaseContainer]


class ContainersFactory:
    @staticmethod
    def get(language: ProgrammingLanguages) -> ContainerClass:
        containers_mapping: t.Mapping[ProgrammingLanguages, ContainerClass] = {
            ProgrammingLanguages.PYTHON: PythonContainer,
            ProgrammingLanguages.PYPY: PyPyContainer,
            ProgrammingLanguages.CPP: CppContainer,
            ProgrammingLanguages.PASCAL_ABC: PascalABCContainer
        }

        class_ = containers_mapping.get(language, None)
        if class_ is None:
            raise ValueError(f'Language {language} is not specified in mapping!')
        return class_
