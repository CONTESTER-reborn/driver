import typing as t

from libs.containers._base_containers import _BaseContainer
from libs.containers.all_containers import PythonContainer, PyPyContainer, CppContainer, PascalABCContainer
from libs.enums import ProgrammingLanguages

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
        return containers_mapping.get(language)
