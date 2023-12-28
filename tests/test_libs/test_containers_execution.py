from abc import ABC, abstractmethod

import pytest

from driver.libs.containers import ContainersFactory, _BaseContainer
from driver.libs.enums import DriverError, ProgrammingLanguage
from driver.libs.files import FileCreator
from driver.libs.types import CodeExecutionCommandOptions, ProcessedContainerExecutionResult


class BaseTestContainer(ABC):

    @pytest.fixture(scope='class')
    def container(self):
        ContainerClass = ContainersFactory.get(self._programming_language)
        container = ContainerClass(time_limit=1, memory_limit='128m')
        with container:
            yield container

    @property
    @abstractmethod
    def _programming_language(self) -> ProgrammingLanguage:
        """Source code that can be executed successfully"""
        pass

    @abstractmethod
    def test_success(self, container: _BaseContainer) -> None:
        """Source code that can be executed successfully"""
        pass

    @abstractmethod
    def test_runtime_error(self, container: _BaseContainer) -> None:
        """Source code that raises an error during run-time"""
        pass

    @abstractmethod
    def test_time_limit_error(self, container: _BaseContainer) -> None:
        """Source code that raises time limit error"""
        pass

    def run_source_code(self, source_code: str, container: _BaseContainer) -> ProcessedContainerExecutionResult:
        with FileCreator(source_code, self._programming_language) as file_creator:
            execution_options = CodeExecutionCommandOptions(filename=file_creator.filename, stdin='')
            return container.execute(execution_options)


class BaseInterpretedTestContainer(BaseTestContainer, ABC):
    ...


class BaseCompiledTestContainer(BaseTestContainer, ABC):
    @abstractmethod
    def test_compilation_error_execution(self, container: _BaseContainer) -> None:
        """Source code that raises compilation error"""
        pass


class TestInterpretedContainer(BaseInterpretedTestContainer):
    @property
    def _programming_language(self) -> ProgrammingLanguage:
        return ProgrammingLanguage.PYTHON

    def test_success(self, container) -> None:
        code = 'print("Hello World!")'
        result = self.run_source_code(code, container)

        assert result.exit_code == 0
        assert result.output == "Hello World!"
        assert result.execution_time > 0
        assert result.error_message == ''

    def test_runtime_error(self, container: _BaseContainer) -> None:
        code = 'print(1 / 0)'
        result = self.run_source_code(code, container)

        assert result.exit_code != 0
        assert result.output != ''
        assert result.execution_time == 0
        assert result.error_message == DriverError.RUNTIME_ERROR.value.message

    def test_time_limit_error(self, container: _BaseContainer) -> None:
        code = 'from time import sleep\nsleep(100)'
        result = self.run_source_code(code, container)

        assert result.exit_code == 15
        assert result.output != 0
        assert result.execution_time == 0
        assert result.error_message == DriverError.TIME_LIMIT_EXCEEDED.value.message


class TestCompiledContainer(BaseCompiledTestContainer):
    @property
    def _programming_language(self) -> ProgrammingLanguage:
        return ProgrammingLanguage.CPP

    def test_success(self, container: _BaseContainer) -> None:
        code = '#include <iostream>\n\nint main() {\n\tstd::cout << "Hello World!\\n";\n\treturn 0;}'
        print(code)
        result = self.run_source_code(code, container)

        assert result.exit_code == 0
        assert result.output == "Hello World!"
        assert result.execution_time >= 0
        assert result.error_message == ''

    def test_runtime_error(self, container: _BaseContainer) -> None:
        # Division by zero
        function_content = '\n\tint a = 1;\n\tint b = 0;\n\tint c = a / b;\n\treturn 0;'
        code = f'#include <iostream>\n\nint main() {{{function_content}}}'
        result = self.run_source_code(code, container)

        assert result.exit_code != 0
        assert result.execution_time == 0
        assert result.error_message == DriverError.RUNTIME_ERROR.value.message

    def test_time_limit_error(self, container: _BaseContainer) -> None:
        func_code = '\n\tstd::this_thread::sleep_for(std::chrono::seconds(10));\n\treturn 0;'
        code = f'#include <iostream>\n#include <thread>\n#include <chrono>\n\nint main() {{{func_code}}}'
        result = self.run_source_code(code, container)

        assert result.exit_code == 15
        assert result.output == ''
        assert result.execution_time == 0
        assert result.error_message == DriverError.TIME_LIMIT_EXCEEDED.value.message

    def test_compilation_error_execution(self, container: _BaseContainer) -> None:
        # No semicolons (";")
        code = '#include <iostream>\n\nint main() {\n\tstd::cout << "Hello world!\\n"\n\treturn 0}'
        result = self.run_source_code(code, container)

        assert result.exit_code == 1
        assert result.output != ''
        assert result.execution_time == 0
        assert result.error_message == DriverError.COMPILATION_ERROR.value.message
