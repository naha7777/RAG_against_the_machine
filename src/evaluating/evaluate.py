import json
from typing import Any


def evaluator(my_answers_path: str, ref_answers_path: str) -> None:
    with open(my_answers_path, "r") as f:
        my_file = json.load(f)
    with open(ref_answers_path, "r") as f:
        reference_file = json.load(f)

    for key, v in my_file.items():
        if key == "k":
            k = v
        else:
            search_results = v

    for key, v in reference_file.items():
        rag_questions = v

    for i in range(len(rag_questions)):
        reference = rag_questions[i]
        my_research = search_results[i]
        for key, v in reference.items():
            if key == 'sources':
                ref_sources = v
        if ref_sources:
            i_chunk_lst = []
            for src in ref_sources:
                for key, value in src.items():
                    if key == 'file_path':
                        ref_file_path = value
                    elif key == 'first_character_index':
                        ref_first = value
                    elif key == 'last_character_index':
                        ref_last = value
                for key, val in my_research.items():
                    if key == "retrieved_sources":
                        if len(ref_sources) <= 1:
                            i_chunks = find_chunks(ref_file_path, val, k)
                        else:
                            i_chunk_lst.append(find_chunks(ref_file_path, val,
                                                           k))
            # on sort de la boucle
            # soit on a une liste de listes de chunks (si plrs refs/src)
            # pour 2 refs par ex : [[0, 5, 10], [3, 4, 6]]
            # soit on a une liste de chunks (si une seule ref/src)
            # ex : [0, 1, 2, 3, 4]
            # notre but c'est de mettre cette liste dans une fonction qui
            # calcule le recall@1, le recall@3, le recall@5, le recall@10
            # si ya assez de k pour ca
            if len(ref_sources) <= 1:
                recall(i_chunks, k)
            elif len(ref_sources) > 1 and i_chunk_lst != []:
                recall(i_chunk_lst, k)
        else:
            raise ValueError("can't find sources")


def find_chunks(ref_file: str, retrieved_sources: list[dict[str, Any]],
                k: int) -> list[int]:
    chunk_index_list = []
    n = 0
    while n < k:
        src = retrieved_sources[n]
        for key, value in src.items():
            if value == ref_file:
                chunk_index_list.append(n)
        n += 1
    return chunk_index_list


def recall(chunk_lst: list[int] | list[list[int]], k: int) -> None:
    pass

# Le recall@5 ne compare pas "5 chunks contre 5 chunks". Pour chaque question,
# on regarde si au moins une des sources de référence est retrouvée parmi les k
# premiers résultats. Avec une seule source de référence, c'est simplement
# "est-ce que ce passage est dans mes 5 premiers?"

# Pour une question :
# recall@k = (nb de sources de référence retrouvées dans le tok k) /
# (nombre de sources de référence)

# 1 source de référence, retrouvée dans le top 5 = 1/1 = 1
# 1 source de référence, pas retrouvée = 0/1 = 0
# 2 sources de référence, 1 retrouvée = 1/2 = 0.5 Le score global est la
# moyenne sur toutes les questions.
# Si recall@5 = 84% cela signifique que 84% des questions ont leur source dans
# les 5 premiers résultats.

# meme fichier (file_path identique)
# les plages de caractères se recoupent (debut1 <= fin2 et début2 <= fin1)

# probleme si ya plusieurs références
# si le nb est de un ya un appel de recall donc ca va
# si ya plusieurs refs ca veut dire qu'on doit attendre plusieurs appels pour
# faire le calcul
# ou sinon je return quelque chose dans ma fonction recall que je receptionne
# dans une liste crée pour chaque source

# donc la je mets les chunks qui ont le meme file_path que la source dans une
# lst que je renvoie
# donc la fonction s'appelle pas recall mais plutot find_chunks

# une fois qu'on a la liste de chunks, ou les listes si plusieurs ref
