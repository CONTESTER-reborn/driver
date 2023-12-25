from driver.libs.containers import ContainersFactory
from driver.libs.files import FileCreator
from driver.libs.enums import ProgrammingLanguage
from driver.libs.types import CodeExecutionCommandOptions

language = ProgrammingLanguage.PYTHON
Container = ContainersFactory.get(language)
source = """print(1)\nprint(2)\nprint(3)"""

with Container(time_limit=2, memory_limit='128m') as container:
    for _ in range(10):
        with FileCreator(source_code=source, programming_language=language) as file_creator:
            execution_options = CodeExecutionCommandOptions(filename=file_creator.filename, stdin=r'')
            result = container.execute(options=execution_options)
            print(result)
