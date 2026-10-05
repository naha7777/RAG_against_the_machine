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
[chonkie](https://pypi.org/project/chonkie/)\
[chonkie](https://www.reddit.com/r/Rag/comments/1gnxx7i/introducing_chonkie_the_tinybutmighty_rag/?tl=fr)\
[IA](https://www.youtube.com/watch?v=kISRpDfbS4Y&t=328s)\
[RAG](https://www.youtube.com/watch?v=qUHEUXwr_J8&t=371s)\
[Python Fire](https://davidbieber.com/post/2017-03-06-introducing-python-fire/)\
[BM25](https://www.veonum.com/rag-hybride/)\
[recall@k](https://milvus.io/ai-quick-reference/what-is-recallatk)\
[zipfile](https://www.tresfacile.net/le-module-python-zipfile-des-archives-zip/)\
[pathlib](https://www.datacamp.com/fr/tutorial/comprehensive-tutorial-on-using-pathlib-in-python-for-file-system-manipulation)\
[tqdm](https://www.datacamp.com/fr/tutorial/tqdm-python)\
[stemmer](https://www.datacamp.com/fr/tutorial/stemming-lemmatization-python)\
[transformers](https://blog.stephane-robert.info/docs/developper/programmation/python/hugging-face/)

### AI usage

_____________________________________________

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

--------------------------------------------------------------------------------
uv sync

protéger si on lance sans uv / sans venv

mettre dans RAGEngine des vrais datas de base et pas des " " comme j'ai fait

voir pour charger une seule fois le LLM
