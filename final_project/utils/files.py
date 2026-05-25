from enum import StrEnum
import os


class FilePath(StrEnum):
    PREFIX = '@::'
    POSTFIX = '::'


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
    while FilePath.PREFIX in query:
        begin = query.find(FilePath.PREFIX) + 3
        end = query.find(FilePath.POSTFIX, begin + 2)

        file_path = query[begin:end]
        content = read_file(file_path)

        target = FilePath.PREFIX + file_path + FilePath.POSTFIX
        query = query.replace(target, content)
    return query
