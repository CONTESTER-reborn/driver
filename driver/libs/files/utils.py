from driver.libs.types import Filename

def get_compiled_filename(original_filename: Filename, save_extension: bool = False) -> Filename:
    """
    Generates new name for compiled file based of original name

    For example, if original name of your file was `script.cpp`, then the function will return
    `script-compiled.cpp` or `script-compiled`, based on `save_extension` flag.
    Suffix `compiled` can be adjusted
    """
    suffix = 'compiled'
    name, extension = original_filename.split('.')

    if save_extension:
        return f'{name}-{suffix}.{extension}'
    return f'{name}-{suffix}'
