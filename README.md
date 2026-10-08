_This project has been created as part of the 42 curriculum by anacharp._

# RAG Against the Machine

## Description

RAG Against the Machine is a Retrieval-Augmented Generation (RAG) system that answers questions about a codebase (here, vLLM 0.10.1).

Instead of retraining a model to give it new knowledge, we give it access to an external knowledge base. When a question is asked, the system finds the passages of the codebase that are related to it, sends only those passages to a small language model, and asks the model to write the final answer from them. A RAG is, in a way, an external memory where we can put whatever we want the model to know.

A RAG has four steps:

- **Indexing**: read every file of the knowledge base, cut it into chunks and build a searchable index.
- **Retrieving**: given a question, search the index for the k best chunks.
- **Augmenting**: filter the k chunks and insert them in the model's prompt while respecting the token limit.
- **Generating**: the model (`Qwen/Qwen3-0.6B`) reads the context and writes the answer.

## Instructions

### Requirements

- Python (see `.python-version` / `pyproject.toml`)
- [uv](https://docs.astral.sh/uv/)
- The vLLM archive `data/raw/vllm-0.10.1.zip`
- A GPU is optional: the model runs on CUDA if available, otherwise on CPU (much slower).

### Installation

```bash
make install
```

### Commands

All commands are exposed through [Python Fire](https://github.com/google/python-fire) and run with `uv run python -m src <command>`.

| Command | Description |
|---|---|
| `index --max_chunk_size 2000` | Extract the archive, chunk every `.py`, `.md` and `.txt` file, build the BM25 index in `data/processed/` |
| `search --query "<question>" --k 10` | Print the k best sources for one question |
| `search_dataset --dataset_path "<path>" --k 10 --save_directory "<directory>"` | Run the search on a whole dataset and write a `StudentSearchResults` JSON |
| `answer "<question>" --k 10` | Retrieve, then generate an answer with Qwen3-0.6B |
| `answer_dataset --student_search_results_path "<path>" --save_directory "<directory>"` | Generate answers for a whole search-results file |
| `evaluate --student_search_results_path "<path>" --dataset_path "<path>"` | Compute Recall@k against a reference dataset |

Note: the index must be built with `index` before any search or answer command.

## System architecture

```
 vllm-0.10.1.zip
        │  extract
        ▼
   ┌──────────┐   chunks (text, file_path, first/last character index)
   │ Chunker  │ ───────────────────────────────┐
   └──────────┘                                │
        │ tokenize (stopwords + stemming)      ▼
        ▼                              data/processed/chunks.json
   ┌──────────┐
   │   BM25   │ ─────► data/processed/bm25_index
   └──────────┘
        ▲
        │ question (same tokenization)
   ┌──────────┐   top-k chunks    ┌───────────┐   prompt    ┌───────────────┐
   │ Retriever│ ────────────────► │ Augmenting│ ──────────► │ Qwen3-0.6B    │ ──► answer
   └──────────┘                   └───────────┘             └───────────────┘
```

Main components (all under `src/`):

- **`indexer/`**: `Chunker` (archive extraction and chunking) and `indexer` (tokenization, BM25 index, `chunks.json`).
- **`retriever/`**: loads the index and the chunks, returns the k best chunks for a query.
- **`answering/`**: `GetAnswer` builds the prompt within the token budget and calls the model.
- **`models.py`**: Pydantic models (`MinimalSource`, `MinimalSearchResults`, `StudentSearchResults`, `MinimalAnswer`, `StudentSearchResultsAndAnswer`, `UnansweredQuestion`, `AnsweredQuestion`, `RagDataset`) that define the structure of every JSON output.
- **`RAGEngine.py`**: the class exposed through Fire; it validates the arguments and chains the components.

The index is built once by `index` and only loaded by the other commands. Each chunk is stored as a dictionary, and the position of a chunk in the list is the identifier returned by BM25.

## Chunking strategy

Two strategies are used, depending on the type of file. Files that are neither code nor documentation are ignored. Both rely on the [Chonkie](https://pypi.org/project/chonkie/) library, and the maximum chunk size is 2000 characters.

### Python files

`chunk_code_file` uses Chonkie's `CodeChunker` (`chonkie[code]`) with `language="python"`. It cuts along the structure of the code (functions, classes) instead of at arbitrary positions, so a chunk is usually a coherent unit.

### Markdown and text files

`chunk_docs_file` uses Chonkie's `RecursiveChunker`. For `.md` files, the `markdown` recipe is used so that the cuts follow headings, paragraphs and lists first, and only then lines and sentences. For `.txt` files, the default recursive rules are used.

### Chunk metadata

Each chunk keeps its text, its file path and the **first and last character indexes** in the original file. These positions are needed to compare a retrieved chunk with a reference source, so they are taken from the chunker and checked: the text of a chunk must be equal to `file_content[first:last]`.

### Overlap

I tested adding a small overlap between neighbouring chunks (5%), but it is not used in the final version: it makes chunks larger than their source passages, which lowers the IoU used by the evaluation, and the structure-aware chunkers already avoid most cuts in the middle of a unit.

## Retrieval method

I chose **BM25**, a ranking function used by search engines to estimate how relevant a document is to a query. It is an improved version of TF-IDF and is very common in RAG systems. For each word of the query, BM25 computes a score from three ingredients:

- **Term frequency (TF) with saturation**: the more a word appears in a chunk, the more relevant the chunk is, but with diminishing returns. Using a word 100 times does not make a chunk ten times more relevant than using it 10 times.
- **Inverse document frequency (IDF)**: rare words weigh more than common ones. A word like "and" has a very low weight, a specific identifier has a high one.
- **Length normalization**: a long chunk is more likely to contain the query words by chance, so BM25 penalizes long chunks.

The score of a chunk is the sum of the scores of the query words, and chunks are ranked by decreasing score.

### How BM25 is used

BM25 is used in two distinct phases.

**Indexing** (once, no question needed):

```python
tokens = bm25s.tokenize(texts, stopwords="en", stemmer=stemmer)
retriever = bm25s.BM25()
retriever.index(tokens)
retriever.save("data/processed/bm25_index")
```

The list of chunks (text, path, positions) is saved separately in `data/processed/chunks.json`, in the same order as the indexed texts.

**Searching** (for each question):

```python
retriever = bm25s.BM25.load("data/processed/bm25_index")
query_tokens = bm25s.tokenize(query, stopwords="en", stemmer=stemmer)
indexes, scores = retriever.retrieve(query_tokens, k=k)
best_chunks = [chunks[i] for i in indexes[0]]
```

BM25 only returns the **positions** of the best chunks; they are used to look up the full chunks in `chunks.json`. The tokenization (stopwords, English stemmer) must be strictly identical at indexing and at search time.

## Augmenting and generation

- The retrieved chunks are added to the prompt from the most to the least relevant, as long as the total stays under the token budget (`context_limite`, 3000 tokens by default, counted with the Qwen tokenizer). The best chunk is placed last, right before the question, because a small model pays more attention to the end of the prompt.
- The prompt is built with Qwen's chat template. A system message asks for a short answer based only on the context.
- The model is `Qwen/Qwen3-0.6B`, loaded once per run, on GPU when available. Thinking mode is disabled and the answer is limited to 150 new tokens.
- The answer is returned together with its sources in a structured JSON validated by the Pydantic models.

## Performance analysis

Measured on the private datasets with the provided moulinette (`evaluate_student_search_results`, `k=10`, `max_context_length=2000`):

| Metric | Docs | Code |
|---|---|---|
| Recall@1 | 0.62 | 0.28 |
| Recall@3 | 0.76 | 0.43 |
| Recall@5 | **0.83** (goal ≥ 0.80) | **0.51** (goal ≥ 0.50) |
| Recall@10 | 0.88 | 0.57 |

A source is considered found when one retrieved chunk is in the same file and its character range has an IoU of at least 0.05 with the reference range.

System performance (on the exam script `exams/scripts/exam_retrieval.sh`):

- Indexing of the whole vLLM archive: about 54 s (limit: 300 s).
- Retrieval of 200 questions (docs and code): about 21 s (limit: 90 s), because the index and the chunks are loaded once and not for each question.
- Answer generation is much slower than retrieval: roughly 40 s per question on CPU, and much faster on GPU.

Code questions are harder than documentation questions: identifiers such as `snake_case` or `CamelCase` names are not well split by the default tokenizer, and many source passages are very short compared to a chunk, which lowers the IoU.

## Design decisions

- **BM25 instead of embeddings**: fast to index, no model to download for retrieval, and very good when questions contain exact identifiers and keywords.
- **Index once, load once**: the index and `chunks.json` are saved on disk and loaded a single time per command, which keeps `search_dataset` fast.
- **Chunks stored as dictionaries**: BM25 returns positions only, so the text, the path and the character indexes are kept in a separate file in the same order.
- **Real positions from the chunker**: the character indexes come from the chunker and are verified against the file content. Computing them from the chunk size gave wrong ranges and a much lower recall.
- **Two chunking strategies**: structure-aware cuts for code, heading-aware cuts for documentation.
- **Strict argument validation**: every command checks its parameters and raises a clear error message (colored with `rich`) instead of a traceback.

## Challenges faced

- **Wrong chunk positions**: my first version computed the positions by assuming every chunk had the maximum size. The recall was low even when the right passage was retrieved. Using the real positions of the chunks solved it.
- **Understanding the evaluation**: my own recall was higher than the moulinette's because I accepted any overlap. The subject requires an IoU ≥ 0.05, which I implemented in `evaluate`.
- **Generation quality of a 0.6B model**: answers could be vague or too long. Fixes: a short system prompt, the best chunk placed right before the question, a smaller `max_new_tokens`, and deterministic generation.
- **Slow generation**: the model initially ran on CPU only. Moving it to the GPU when available greatly reduced the time per question.
- **Disk quota**: caches (Hugging Face, Triton, uv) filled the home directory. They were redirected to a larger disk using environment variables (`HF_HOME`, `TRITON_CACHE_DIR`, `UV_CACHE_DIR`).
- **Typing**: the `transformers` stubs make `mypy` complain about model methods; the model is typed as `Any` where needed.

## Example usage

Build the index:

```bash
uv run python -m src index --max_chunk_size 2000
```

Search for one question:

```bash
uv run python -m src search "What is the default value of trust_remote_code in the LLM class?" --k 10
```

Answer one question:

```bash
uv run python -m src answer "What is the default value of trust_remote_code in the LLM class?" --k 10
```

Search a whole dataset, then answer it:

```bash
uv run python -m src search_dataset \
  --dataset_path data/datasets/public/UnansweredQuestions/dataset_docs_public.json \
  --k 10 \
  --save_directory data/output/search_results/UnansweredQuestions

uv run python -m src answer_dataset \
  --student_search_results_path data/output/search_results/UnansweredQuestions/dataset_docs_public.json \
  --save_directory data/output/search_results_and_answer/UnansweredQuestions
```

Evaluate the recall:

```bash
uv run python -m src evaluate \
  --student_search_results_path data/output/search_results/UnansweredQuestions/dataset_docs_public.json \
  --dataset_path data/datasets/public/AnsweredQuestions/dataset_docs_public.json
```

Note: each option must be written `--name value` (or `--name=value`) on the same command line or with a trailing `\` and no space after it.

## Resources

### Documentation

- [Chonkie (PyPI)](https://pypi.org/project/chonkie/)
- [Introducing Chonkie (Reddit)](https://www.reddit.com/r/Rag/comments/1gnxx7i/introducing_chonkie_the_tinybutmighty_rag/?tl=fr)
- [RAG explained (video)](https://www.youtube.com/watch?v=qUHEUXwr_J8&t=371s)
- [AI introduction (video)](https://www.youtube.com/watch?v=kISRpDfbS4Y&t=328s)
- [Python Fire](https://davidbieber.com/post/2017-03-06-introducing-python-fire/)
- [BM25](https://www.veonum.com/rag-hybride/)
- [Recall@k](https://milvus.io/ai-quick-reference/what-is-recallatk)
- [zipfile](https://www.tresfacile.net/le-module-python-zipfile-des-archives-zip/)
- [pathlib](https://www.datacamp.com/fr/tutorial/comprehensive-tutorial-on-using-pathlib-in-python-for-file-system-manipulation)
- [tqdm](https://www.datacamp.com/fr/tutorial/tqdm-python)
- [Stemming and lemmatization](https://www.datacamp.com/fr/tutorial/stemming-lemmatization-python)
- [Transformers (Hugging Face)](https://blog.stephane-robert.info/docs/developper/programmation/python/hugging-face/)

### AI usage

I used an AI assistant during this project, for:

- explaining concepts (how BM25 builds and uses its index, how Fire parses arguments, how recall@k and IoU work);
- debugging errors (shell line continuation, import paths, exceptions, `mypy` messages, disk-space and GPU issues);
- reviewing my code and suggesting improvements (chunk positions, prompt structure, evaluation logic);
- helping to write and proofread this README.
