# utiliser pydantic pour mettre en stdout un json sans le créer
# id de la question
# la question
# les retrieved sources (autant qu'il y a de K) :
# le filepath, le first_character_index et le last
# puis le nombre de k

# pour ca on envoie la question a BM25 avec k
# BM25 nous donne les K meilleurs chunks
# on retrouve toutes les infos qu'on veut dans le JSON

# j'extrais le contenu du JSON qui est une liste
# grace aux index donnés par BM25 je peux parcourir ma liste et trouver
# les infos nécessaires

import bm25s
import Stemmer
import json
import os
from typing import Any
from pathlib import Path
from src.models import MinimalSource, MinimalSearchResults


def retriever(query: str, k: int) -> None:
    retriever = bm25s.BM25.load("././data/processed/bm25_index",
                                load_corpus=True)

    stemmer = Stemmer.Stemmer('english')

    query_tokens = bm25s.tokenize(query, stopwords="en", stemmer=stemmer)
    index, score = retriever.retrieve(query_tokens=query_tokens, k=k)

    check_file = Path("././data/processed/chunks.json")
    if check_file.exists() is False:
        raise ValueError("can't find data/processed/chunks.json, index please")
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

    for c in best_chunks:
        src = MinimalSource(file_path=c['file_path'].strip('././'),
                            first_character_index=c['first_character_index'],
                            last_character_index=c['last_character_index'])
        retrieved_sources.append(src)

    min_search_res = MinimalSearchResults(question_id="1",
                                          question=query,
                                          retrieved_sources=retrieved_sources)
    minimal_dict = min_search_res.model_dump_json(indent=4)
    print(minimal_dict)
