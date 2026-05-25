from typing import Literal, TypedDict

PARAGRAPH: Literal['paragraph'] = 'paragraph'
LENGTH: Literal['length'] = 'length'
FORCE: Literal['force'] = 'force'


class FileChunkParams(TypedDict):
    paragraph: int | None
    length: int | None
    force: bool


class ParamsException(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


def format_file_chunk_params(raw_params: str) -> FileChunkParams:
    params = FileChunkParams(paragraph=None, length=None, force=False)
    for param in raw_params.split():
        if param == '-y':
            params[FORCE] = True
            continue
        if '=' not in param:
            raise ParamsException(f'Invalid parameter "{param}"')
        key, value = param.split('=', 1)
        if key == PARAGRAPH:
            params[PARAGRAPH] = int(value)
        elif key == LENGTH:
            params[LENGTH] = int(value)
        else:
            raise ParamsException(f'Unknown parameter "{key}"')
    return params


def _divide_by_paragraphs(raw_chunks: str, count: int) -> list[str]:
    paragraphs = raw_chunks.split('\n')
    chunks = []
    while paragraphs:
        chunks.append('\n'.join(paragraphs[:count]))
        paragraphs = paragraphs[count:]
    return chunks


def _divide_by_length(raw_chunks: str, length: int) -> list[str]:
    chunks = []
    while raw_chunks:
        chunks.append(raw_chunks[:length])
        raw_chunks = raw_chunks[length:]
    return chunks


def divide_by_chunks(raw_chunks: str, params: FileChunkParams) -> list[str]:
    paragraph = params[PARAGRAPH]
    if paragraph is not None:
        return _divide_by_paragraphs(raw_chunks, paragraph)
    length = params[LENGTH]
    if length is not None:
        return _divide_by_length(raw_chunks, length)
    return raw_chunks.split('\n')
