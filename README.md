_This project has been created as part of the 42 curriculum by anacharp_

# RAG against the machine

## Description

## Instructions

## System architecture
Describe your RAG pipeline components and how they
interact

## Chunking strategy
Explain your approach to document segmentation

## Retrieval method
Detail the retrieval algorithm and ranking mechanism

## Performance analysis
Discuss recall@k scores and system performance

## Design decisions
Explain key implementation choices

## Challenges faced
Document difficulties encountered and solutions

## Example usage
Provide clear examples of running your system

## Resources

### Documentation
[chonkie](https://pypi.org/project/chonkie/)
[IA](https://www.youtube.com/watch?v=kISRpDfbS4Y&t=328s)
[RAG](https://www.youtube.com/watch?v=qUHEUXwr_J8&t=371s)
[Python Fire](https://davidbieber.com/post/2017-03-06-introducing-python-fire/)
[BM25](https://www.veonum.com/rag-hybride/)
[recall@k](https://milvus.io/ai-quick-reference/what-is-recallatk)
[zipfile](https://www.tresfacile.net/le-module-python-zipfile-des-archives-zip/)

### AI usage

_____________________________________________

Modèles de données (Pydantic) : le sujet impose des classes précises pour valider les échanges entre étapes :
- `MinimalSource` (file_path + indices de caractères)
- `UnansweredQuestion`/`AnsweredQuestion`
- `RagDataset`
- `MinimalSearchResults`/`MinimalAnswer`
- `StudentSearchResults`/`StudentSearchResultAndAnswer` (format de sortie attendu)

Evaluation : recall@k
- pour chaque question, on regarde la proportion des sources correctes retrouvées parmi les k premiers resultats
- une source est 'trouvée' si le file_path est exactement identique et si l'intervalle de caractères a un IoU (Intersection over Union) >= 0.05 avec la référence (seuil bas, donc pas besoin de matcher exactement les indices)
- seuils à atteindre : >= 80% recall@5 sur les questions "docs", >=50% recall@5 sur les questions "code"

Contraintes de perf :
- indexation : max 5 minutes pour tout le corpus
- recherche : max 90 secondes pour 200 questions

Exigences techniques générales :
- python3.10, flake8, mypy, docstrings
- gestion propre des erreurs (try except) - aucun crash
- uv comme gestionnaire de paquets
- CLI avec Python Fire : chaque commande est écrite de cette manière : uv run python -m src <command> [options]:
	- index –max_chunk_size <int> = chunk tout data/raw/ et crée un index dans data/processed
	- search <query> –k <int> = retourne les meilleurs chunks pour une question
	- search_dataset –dataset_path <path> –k <int> –save_directory <dir> = lance la recherche dans un jeu de données et écrit un JSON StudentSearchResults
	- answer <query> –k <int> = répond a une question en utilisant le retrieved context
	- answer_dataset –student_search_results_path <path> –save_directory <dir> = génère les réponses pour un jeu de données en produisant un JSON StudentSearchResultsAndAnswer
	- evaluate –student_search_results_path <path> –dataset_path <path> = cela rapporte mon propre recall@k par rapport à un jeu de données de référence pour mes propres tests
- tqdm pour les barres de progression
- un makefile avec les regles install, run, debug, clean, lint, lint-strict

Structure repo :
```bash
src/                  → implémentation
pyproject.toml, uv.lock
README.md
data/raw/             → corpus source (vLLM)
data/processed/       → index généré
data/datasets/{UnansweredQuestions,AnsweredQuestions}/
data/output/search_results/<scope>/
data/output/search_results_and_answer/<scope>/
```
Ces chemins doivent tous être configurables en CLI, jamais codés en dur, car le correcteur lance une pipeline automatisée : index -> search_dataset -> moulinette evaluate_student_search_results

Points de vigilance particuliers :
- le file_path doit matcher EXACTEMENT le chemin du corpus (ex: data/raw/vllm-0.10.1/docs/features/lora.md) -> un resultat dans le mauvais fichier ne compte jamais
- ne jamais depasser 2000 caracteres par chunk
- la moulinette ne doit jamais etre appelee/importee dans le code, la commande evaluate du CLI sert seulement au debuggage
- modeles pydantic fournis sont une base extensible, possibilite d'ajouter des modeles etc

EN GROS

- On a plein de fichiers genre des .py, des .md etc qu'il faut chunker, chaque chunk fait 2000 caracteres max, on chunk differemment un python .py qu'un mardown .md ou qu'un .txt.
Faut aussi faire gaffe à couper au bon endroit et à avoir le contexte genre overlap un peu devant et derriere
Pour chunker ya le paquet chonkie
- une fois qu'on a chunke, on utilise BM25 qui degage les mots nuls du genre 'a', 'de', 'un' et qui classe selon l'occurence du mot pour savoir l'importance, il met au dessus les mots qui reviennent le plus souvent
- ensuite on prompte le llm en mode t'es un codeur etc

installer transformers pour mettre Qwen en 2/3 lignes

--------------------------------------------------------------------------------
uv sync

Gérer dossiers/fichiers absent, pas les permissions

INDEX REPOSITORY :
- extraire le vllm-0.10.1.zip si il est présent dans data/raw/ (si non le telecharger et le placer dnas le dossier)
- CHUNKING :
	- Créer une boucle qui parcourt les dossiers
	- si le fichier se termine par .md on applique RecursiveChunker.from_recipe("markdown")
	- si le fichier se termine par .py ou .c on applique le CodeChunker(language=" ")
	- rassembler tous les chunks dans une seule grande base de donnée (liste python ? / fichier ?) qu'on passe à bm25 pour créer l'index de recherche
- BM25 index : créer l'index et le rendre persistant, ne se recrée pas a chaque fois


Quand on pose une question :
- on check si ya l'index
- si non on le crée en moins de 5 min (chunk + bm25)
- top-k chunk (file_path + character indices)
- qwen
- réponse dans un json

4 commandes :
- index the corpus ONCE :
```bash
uv run python -m src index --max_chunk_size 2000
Ingestion complete! Indices saved under data/processed/
```
- search a dataset :
```bash
uv run python -m src search_dataset
--dataset_path data/datasets/UnansweredQuestions/dataset_docs_public.json
--k 10
--save_directory data/output/search_results/UnansweredQuestions
Saved student_search_results to data/output/search_results/UnansweredQuestions/dataset_docs_public.json
```

- score with the moulinette :
```bash
./moulinette evaluate_student_search_results
data/output/search_results/UnansweredQuestions/dataset_docs_public.json
data/datasets/AnsweredQuestions/dataset_docs_public.json
--k 10 --max_context_length 2000
Student data is valid: True
Evaluation Results
========================================
Recall@1: 0.450 Recall@3: 0.590 Recall@5: 0.650 Recall@10: 0.720
```

- générer une réponse :
```bash
uv run python -m src answer_dataset
--student_search_results_path data/output/search_results/UnansweredQuestions/dataset_docs_public.json
--save_directory data/output/search_results_and_answer/UnansweredQuestions
Loaded 100 questions ... Processed 100 of 100 questions
Saved student_search_results_and_answer to .../UnansweredQuestions/dataset_docs_public.json
```

proteger si on lance sans uv / sans venv

meme tokenisation a l'index et search :
tokens = bm25s.tokenize(chunks_text ou query, stopwords="en", stemmer=stemmer)

question → BM25 → "meilleurs chunks : 50, 12, 7..." → récupérer leur texte → LLM → réponse
BM25 ne rédige rien : il classe les chunks. Le LLM reçoit ensuite le texte de ces chunks comme contexte, avec la question.
