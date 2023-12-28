import typing as t

from fastapi import FastAPI, Query

from driver.libs.containers import ContainersFactory
from driver.libs.files import FileCreator
from driver.libs.enums import ProgrammingLanguage
from driver.libs.types import CodeExecutionCommandOptions, ProcessedContainerExecutionResult

app = FastAPI()


@app.post("/execute")
def execute(
        language: str = Query(),
        source_code: str = Query(),
        time_limit: int = Query(),
        memory_limit: str = Query(),
        stdin_list: t.List[str] = Query()
) -> t.List[ProcessedContainerExecutionResult]:
    languages_map = {
        'python': ProgrammingLanguage.PYTHON,
        'pypy': ProgrammingLanguage.PYPY,
        'cpp': ProgrammingLanguage.CPP,
        'pascal-abc': ProgrammingLanguage.PASCAL_ABC,
    }

    print(source_code)

    response = []

    programming_language = languages_map[language]
    Container = ContainersFactory.get(programming_language)
    with Container(time_limit, memory_limit) as container:
        with FileCreator(source_code, programming_language) as fc:
            for stdin in stdin_list:
                execution_options = CodeExecutionCommandOptions(filename=fc.filename, stdin=stdin)
                result = container.execute(options=execution_options)
                response.append(result)
            print('Response is sent')
            return response
