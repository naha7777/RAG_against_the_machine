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

### AI usage

_____________________________________________


BUT DU PROJET :
Construire un systeme de RAG qui repond a des questions sur un codebase.

Idee centrale : plutot que de reentrainer un modele pour lui donner de nouvelles connaissances, on lui donne acces a une source externe de documents et on va chercher les passages pertinents au moment de repondre.

4 etapes de RAG :
1- Indexation : lire les fichiers et les decouper en petits morceaux = chunks avec lesquels construire un index consultable rapidement
2- Recuperation : face a une question, chercher dans l'index les k chunks les plus pertinents
3- Augmentation : filter les k chunks et les inserer dans le contexte du modele (respect de la limite de token)
4- Generation : le modele Qwen3 lit ce contexte et redige une reponse

Chunking = decoupage : deux strategies obligatoires car le code et le texte ne se decoupent pas pareil :
- chunking python
- chunking markdown/texte
- taille max de 2000 caracteres par chunk (configurable via --max_chunk_size, default 2000)

chonkie ou st

Retrieval lexical : implementer au moins une methode parmi :
- TF-IDF (Term Frequency-Inverse Document Frequency) : pondere les mots selon leur frequence dans le document vs dans le corpus
- BM25 : variante plus robuste de TF-IDF, standard en recherche d'information

Ce sont des methodes de recherche par mots-clefs, pas semantique.

Generation : utiliser Qwen3, un petit modele local, pour produire une reponse structuree en JSON a partir du contexte recupere.

Modeles de donnees (Pydantic) : le sujet impose des classes precises pour valider les echanges entre etapes :
- `MinimalSource` (file_path + indices de caractères)
- `UnansweredQuestion`/`AnsweredQuestion`
- `RagDataset`
- `MinimalSearchResults`/`MinimalAnswer`
- `StudentSearchResults`/`StudentSearchResultAndAnswer` (format de sortie attendu)

Evaluation : recall@k
- pour chaque question, on regarde la proportion des sources correctes retrouvees parmi les k premiers resultats
- une source est 'trouvee' si le file_path est exactement identique et si l'intervalle de caracteres a un IoU (Intersection over Union) >= 0.05 avec la reference (seuil bas, donc pas besoin de matcher exactement les indices)
- seuils a atteindre : >= 80% recall@5 sur les questions "docs", >=50% recall@5 sur les questions "code"

Contraintes de perf :
- indexation : max 5 minutes pour tout le corpus
- recherche : max 90 secondes pour 200 questions

Exigences techniques generales :
- python3.10, flake8, mypy, docstrings
- gestion propre des erreurs (try except) - aucun crash
- uv comme gestionnaire de paquets
- CLI avec Python Fire : commandes index, search, search_dataset, answer, answer_dataset, evaluate
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
Ces chemins doivent tous etre configurables en CLI, jamais codes en dur, car le correcteur lance une pipeline automatisee : index -> search_dataset -> moulinette evaluate_student_search_results

Points de vigilance particuliers :
- le fil_path doit matcher EXACTEMENT le chemin du corpus (ex: data/raw/vllm-0.10.1/docs/features/lora.md) -> un resultat dans le mauvais fichier ne compte jamais
- ne jamais depasser 2000 caracteres par chunk
- la moulinette ne doit jamais etre appelee/importee dans le code, la commande evaluate du CLI sert seulement au debuggage
- modeles pydantic fournis sont une base extensible, possibilite d'ajouter dse modeles etc

EN GROS

- On a plein de fichiers genre des .py, des .md etc qu'il faut chunker, chaque chunk fait 2000 caracteres max, donc chunker en paragraphes pour les .md peut etre, chunker en fonctions pour les .c, .py etc et ignorer les autres fichiers jcrois (on chunk differemment un python .py qu'un mardown .md ou qu'un .txt)
Faut aussi faire gaffe a couper au bon endroit et a avoir le contexte genre overlap un peu devant et derriere
Pour chunker ya les paquets chonki ou st
- une fois qu'on a chunke, on utilise BM25 qui degage les mots nuls du genre 'a', 'de', 'un' et qui classe selon l'occurence du mot pour savoir l'importance, il met au dessus les mots qui reviennent le plus souvent
- ensuite on prompte le llm en mode t'es un codeur etc
