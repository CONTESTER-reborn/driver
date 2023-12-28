import pytest
from docker import from_env

from driver.libs.containers import ContainersFactory
from driver.libs.enums import ProgrammingLanguage


@pytest.fixture
def client():
    client = from_env()
    yield client


def test_container_context_menu(client):
    ContainerClass = ContainersFactory.get(language=ProgrammingLanguage.PYTHON)
    with ContainerClass(time_limit=1, memory_limit='128m') as container:
        actual_container = container._container
        assert actual_container in client.containers.list()

    assert actual_container not in client.containers.list()
