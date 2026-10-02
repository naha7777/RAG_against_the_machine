import json
import bm25s
import Stemmer
from tqdm import tqdm
from typing import Any
from src.indexer.chunker import Chunker
from src.utils.display import print_success


def indexer(max_chunk_size: int) -> None:
    # create chunker and stock files paths
    chunker = Chunker()
    try:
        chunker.check_zip()
        file_list = chunker.extract_zip()
    except ValueError as e:
        raise ValueError(e)

    # chunk all files
    chunks: Any = []
    for file in tqdm(file_list, desc="Chunking"):
        try:
            if file.endswith(".py"):
                chunks.extend(chunker.chunk_code_file(max_chunk_size, file))
            elif file.endswith((".md", ".txt")):
                chunks.extend(chunker.chunk_docs_file(max_chunk_size, file))
            else:
                continue
        except ValueError as e:
            raise ValueError(e)

    #  create a stemmer
    stemmer = Stemmer.Stemmer('english')

    if chunks:
        try:
            # tokenize all chunks to create an index
            retriever = bm25s.BM25()
            tokens = bm25s.tokenize([c["text"] for c in chunks],
                                    stopwords="en", stemmer=stemmer)
            retriever.index(tokens)
            retriever.save("data/processed/bm25_index")

            # stock all informations about chunks on a JSON
            json_content = json.dumps(chunks, indent=4)
            with open("data/processed/chunks.json", "w",
                      encoding="utf-8") as f:
                f.write(json_content)

        except ValueError as e:
            raise ValueError(e)
        print_success('Ingestion complete! Indexed all chunks'
                      ' under data/processed/')
