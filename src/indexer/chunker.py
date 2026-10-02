from pathlib import Path
import os
import zipfile
from chonkie import CodeChunker, RecursiveChunker, OverlapRefinery
from src.utils.display import print_success
from typing import Any


overlap = 0.10


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
        if file_path.exists is False:
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
                        file: str) -> list[dict] | None:
        file_content = check_and_read_file(file)

        chunker = CodeChunker(language="python",
                              chunk_size=max_chunk_size)

        chunks_txt = [chunk.text for chunk in chunker.chunk(file_content)]
        return save_chunks_info(chunks_txt, max_chunk_size, file)

    def chunk_docs_file(self, max_chunk_size: int,
                        file: str) -> list[dict] | None:
        file_content = check_and_read_file(file)

        m_chunk_s = max_chunk_size - (int(overlap*max_chunk_size))

        if file.endswith(".md"):
            chunker = RecursiveChunker.from_recipe("markdown", lang="en",
                                                   chunk_size=m_chunk_s)
        else:
            chunker = RecursiveChunker(chunk_size=m_chunk_s)

        refinery = OverlapRefinery(context_size=overlap,
                                   method="justified")

        chunks_obj = chunker.chunk(file_content)
        refined_chunks = refinery(chunks_obj)
        chunks_txt = [chunk.text for chunk in refined_chunks]
        return save_chunks_info(chunks_txt, max_chunk_size, file)


def check_and_read_file(file: str) -> str:
    check_file = Path(file)
    if check_file.exists is False:
        raise ValueError(f"can't find {file}")
    if not os.access(check_file, os.R_OK):
        raise ValueError(f"can't read {file}, please change permissions")

    try:
        with open(file, "r", encoding="utf-8") as f:
            code_source = f.read()
    except Exception as e:
        raise ValueError(str(e))

    return code_source

def save_chunks_info(chunks_txt: list[Any], max_chunk_size: int,
                     file: str) -> list[dict]:
    i = 0
    chunks = []
    for txt in chunks_txt:
        if i != 0:
            i += 1
        chunk = {}
        chunk["text"] = txt
        chunk["file_path"] = file
        chunk["first_character_index"] = str(i)
        i += max_chunk_size
        chunk["last_character_index"] = str(i)
        chunks.append(chunk)
    return chunks
