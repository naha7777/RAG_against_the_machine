import bm25s
import Stemmer
import json
import os
from typing import Any
from pathlib import Path
from src.models import MinimalSource


def retriever(retriever: Any, query: str, k: int,
              verbose: bool) -> list[MinimalSource] | list[Any]:
    """Create a stemmer, tokenize a query and call the retriever to find
    the bests chunks. Read chunks.json to find informations about bests chunks.
    Then stock it on MinimalSource model."""

    stemmer = Stemmer.Stemmer('english')

    query_tokens = bm25s.tokenize(query, stopwords="en", stemmer=stemmer)
    index, score = retriever.retrieve(query_tokens=query_tokens, k=k)

    check_file = Path("././data/processed/chunks.json")
    if check_file.exists() is False:
        raise ValueError("You have to index before")
    if not os.access(check_file, os.R_OK):
        raise ValueError("can't read data/processed/chunks.json,"
                         "please change permissions")
    with open("././data/processed/chunks.json", "r",
              encoding="utf-8") as f:
        chunks_infos = f.read()

    if not chunks_infos:
        raise ValueError("error finding informations about chunks")

    chunks_infos = json.loads(chunks_infos)

    chunks: Any = index[0]
    best_chunks = []
    for nb in chunks:
        best_chunks.append(chunks_infos[nb])

    retrieved_sources: list[MinimalSource] = []

    if verbose is True:
        for c in best_chunks:
            src = MinimalSource(
                file_path=c['file_path'].strip('././'),
                first_character_index=c['first_character_index'],
                last_character_index=c['last_character_index'])
            retrieved_sources.append(src)

        return retrieved_sources
    else:
        return best_chunks
