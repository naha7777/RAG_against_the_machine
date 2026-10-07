from pathlib import Path
import os
import zipfile
from chonkie import CodeChunker, RecursiveChunker, OverlapRefinery
from src.utils.display import print_success
from typing import Any


overlap = 0.05


class Chunker:

    def check_zip(self) -> None:
        # check path
        path_to_folder = "././data/raw/"
        path = Path(path_to_folder)
        if path.exists() is False:
            raise ValueError("path to folder invalid")
        if path.is_dir() is False:
            raise ValueError("this is not a directory")

        # check file
        file = "././data/raw/vllm-0.10.1.zip"
        file_path = Path(file)
        if file_path.exists() is False:
            raise ValueError("can't find vllm-0.10.1.zip")
        if file_path.is_file() is False:
            raise ValueError("this is not a file")
        if not os.access(file_path, os.R_OK):
            raise ValueError("can't read the file, please change permissions")
        if not os.access(file_path, os.X_OK):
            raise ValueError("can't execute the file, "
                             "please change permissions")

    def extract_zip(self) -> list[str] | None:
        # extract zip and return a list with all files paths
        file_list = []
        try:
            with zipfile.ZipFile("././data/raw/vllm-0.10.1.zip", "r") as z:
                z.extractall(path="././data/raw/")
                print_success("All files has been extracted")
                for info in z.infolist():
                    file_list.append(f"././data/raw/{info.filename}")
                return file_list
        except FileNotFoundError:
            raise ValueError("can't find files")

    def chunk_code_file(self, max_chunk_size: int,
                        file: str) -> list[dict[Any, Any]] | None:
        file_content = check_and_read_file(file)

        chunker = CodeChunker(language="python",
                              chunk_size=max_chunk_size)

        return set_chunks_info(list(chunker.chunk(file_content)), file)

    def chunk_docs_file(self, max_chunk_size: int,
                        file: str) -> list[dict[Any, Any]] | None:
        file_content = check_and_read_file(file)

        if file.endswith(".md"):
            chunker = RecursiveChunker.from_recipe("markdown", lang="en",
                                                   chunk_size=max_chunk_size)
        else:
            chunker = RecursiveChunker(chunk_size=max_chunk_size)

        chunks_obj = list(chunker.chunk(file_content))
        chunks = set_chunks_info(chunks_obj, file)
        for c in chunks:
            real = file_content[c["first_character_index"]:c["last_character_index"]]
            if real != c["text"]:
                raise ValueError(f"bad positions in {c['file_path']}")
        return chunks


def check_and_read_file(file: str) -> str:
    check_file = Path(file)
    if check_file.exists() is False:
        raise ValueError(f"can't find {file}")
    if not os.access(check_file, os.R_OK):
        raise ValueError(f"can't read {file}, please change permissions")

    try:
        with open(file, "r", encoding="utf-8") as f:
            code_source = f.read()
    except Exception as e:
        raise ValueError(str(e))

    return code_source


def set_chunks_info(chunks_obj: list[Any],
                    file: str) -> list[dict[Any, Any]]:
    chunks = []
    for c in chunks_obj:
        chunk = {}
        chunk["text"] = c.text
        chunk["file_path"] = file
        chunk["first_character_index"] = c.start_index
        chunk["last_character_index"] = c.end_index
        chunks.append(chunk)
    return chunks
