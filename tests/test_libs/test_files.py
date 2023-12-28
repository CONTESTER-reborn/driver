import os

from driver.config import LOCAL_USER_SCRIPTS_DIR
from driver.libs.enums import ProgrammingLanguage
from driver.libs.files import FileCreator
from driver.libs.files.utils import get_compiled_filename


def test_file_creator_context_menu():
    source_code = 'print(1)'

    with FileCreator(source_code, ProgrammingLanguage.PYTHON) as file_creator:
        path_to_file = LOCAL_USER_SCRIPTS_DIR / file_creator.filename
        
        # File should exist
        assert os.path.exists(path_to_file)
        # File should have correct extension
        assert 'py' in file_creator.filename

        with open(path_to_file) as created_file:
            file_content = created_file.read()
            # File should have correct content
            assert file_content == source_code

    # After exiting FileCreator context menu file should be deleted
    assert not os.path.exists(path_to_file)


def test_get_compiled_filename():
    original_filename = 'script-name.cpp'

    compiled_filename = get_compiled_filename(original_filename, save_extension=True)
    assert compiled_filename == 'script-name-compiled.cpp'

    compiled_filename = get_compiled_filename(original_filename, save_extension=False)
    assert compiled_filename == 'script-name-compiled'
