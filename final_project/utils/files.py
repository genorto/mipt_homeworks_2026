import os

FILE_PATH_PREFIX = '@::'
FILE_PATH_POSTFIX = '::'
MAX_FILE_SIZE = 5 * 1024 * 1024


class FileException(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


def read_file(path: str) -> str:
    try:
        if os.path.getsize(path) > MAX_FILE_SIZE:
            raise FileException(f'File "{path}" is bigger than 5 MB.')
        with open(path) as file:
            return file.read()
    except FileNotFoundError as e:
        raise FileException(f'File "{path}" not found.') from e


def insert_files(query: str) -> str:
    while FILE_PATH_PREFIX in query:
        begin = query.find(FILE_PATH_PREFIX) + 3
        end = query.find(FILE_PATH_POSTFIX, begin + 2)
        file_path = query[begin:end]
        content = read_file(file_path)
        target = FILE_PATH_PREFIX + file_path + FILE_PATH_POSTFIX
        query = query.replace(target, content)
    return query
