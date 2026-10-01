from src.indexer.chunker import Chunker
from tqdm import tqdm
from src.utils.display import print_success
import json
import bm25s
import Stemmer


def indexer(max_chunk_size: int) -> None:
    chunker = Chunker()
    try:
        chunker.check_zip()
        file_list = chunker.extract_zip()
    except ValueError as e:
        raise ValueError(e)

    chunks: list[dict] = []
    for file in tqdm(file_list, desc="Chunking"):
        try:
            if file.endswith(".py"):
                chunks.extend(chunker.chunk_code_file(max_chunk_size,
                                                          file))
            # elif file.endswith(".md") or file.endswith(".txt"):
            #     chunk_list.extend(chunker.chunk_docs_file(max_chunk_size,
            #                                               file))
            else:
                pass
        except ValueError as e:
            raise ValueError(e)

    stemmer = Stemmer.Stemmer('english')

    if chunks:
        try:
            retriever = bm25s.BM25()
            tokens = bm25s.tokenize([c["text"] for c in chunks],
                                    stopwords="en", stemmer=stemmer)
            retriever.index(tokens)
            retriever.save("data/processed/bm25_index")

            with open("data/processed/chunks.json", "w", encoding="utf-8") as f:
                json.dump(chunks, f)
        except ValueError as e:
            raise ValueError(e)
        print_success('Ingestion complete! Indexed all chunks'
                        ' under data/processed/')
