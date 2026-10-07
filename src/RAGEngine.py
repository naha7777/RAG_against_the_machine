from src.indexer.index import indexer
from src.retriever.retrieving import retriever
from src.answering.answer import GetAnswer
from src.models import (MinimalSearchResults, StudentSearchResults,
                        MinimalAnswer, MinimalSource,
                        StudentSearchResultsAndAnswer)
from src.utils.check import check_path, check_int, check_json, check_query
from src.evaluating.evaluate import evaluator
from pathlib import Path
from typing import Any
from tqdm import tqdm
import os
import json
import bm25s


dataset_path = "data/datasets/public/UnansweredQuestions/"\
               "dataset_docs_public.json"
save_directory = "data/output/search_results/UnansweredQuestions"
student_search_results_path = "data/output/search_results/"\
                              "UnansweredQuestions/dataset_docs_public.json"
save_answer_dir = "data/output/search_results_and_answer/UnansweredQuestions"
my_file = "data/output/search_results/UnansweredQuestions/"\
          "dataset_docs_public.json"
ref_file = "data/datasets/public/AnsweredQuestions/dataset_docs_public.json"


class RAGEngine:

    def index(self, max_chunk_size: int = 2000) -> None:
        # check if max_chunk_size is valide and call indexer function
        check_int("max_chunk_size", max_chunk_size)
        indexer(max_chunk_size)

    def search(self, query: str = "", k: int = 10,
               verbose: bool = True) -> None:
        # check if query and k are valide
        check_query(query)
        check_int("k", k)

        # load bm25 and call retriever function
        bm25 = load_bm()
        retrieved_sources = retriever(bm25, query, k, True)

        # stock infos on MinimalSearchResults model
        min_search_res = MinimalSearchResults(
            question_id="1",
            question=query,
            retrieved_sources=retrieved_sources)
        minimal_dict = min_search_res.model_dump_json(indent=4)

        #  print a json
        if verbose is True:
            print(minimal_dict)

    def search_dataset(self,
                       dataset_path: str = dataset_path,
                       k: int = 10,
                       save_directory: str = save_directory,
                       verbose: bool = True) -> None:
        # check if path, k, and directory are valide
        check_path(dataset_path)
        check_int("k", k)
        if not save_directory:
            raise ValueError("save_directory must have a name to be create")

        # read the dataset document
        with open(dataset_path, "r", encoding="utf-8") as f:
            datasets_info = f.read()
        datasets_info = json.loads(datasets_info)

        search_res_list = []
        # load bm25 and call the retriever for each question on dataset
        # and stock it on MinimalSearchResults model
        bm25 = load_bm()
        for data in datasets_info["rag_questions"]:
            retrieved_sources = retriever(bm25, data["question"], k, True)
            min_search_res = MinimalSearchResults(
                question_id=data["question_id"],
                question=data["question"],
                retrieved_sources=retrieved_sources)
            search_res_list.append(min_search_res)

        # stock all MinimalSearchResults models on StudentSearchResults model
        stud_search_res = StudentSearchResults(search_results=search_res_list,
                                               k=k)

        # find the file name to create the final json
        file_name = check_json(dataset_path)

        # final json creation
        if verbose is True:
            create_json(save_directory, file_name, stud_search_res)
            print(f"Saved student_search_results to {save_directory}"
                  f"/{file_name}")

    def answer(self, query: str = "", k: int = 10,
               context_limite: int = 3000) -> None:
        # check if query, k and context limite are valide
        check_query(query)
        check_int("k", k)
        check_int("context", context_limite)

        # load bm25 and call retriever function
        bm25 = load_bm()
        best_chunks: list[Any] = retriever(bm25, query, k, False)

        # Create and tokenize a prompt to send it to Qwen 3 and collect answer
        get_answer = GetAnswer()
        tokens = get_answer.augmente(query, best_chunks, context_limite)
        answer = get_answer.generate(tokens)

        # stock informations about all chunks for this question
        retrieved_sources: list[MinimalSource] = []
        for c in best_chunks:
            src = MinimalSource(
                file_path=c['file_path'].strip('././'),
                first_character_index=c['first_character_index'],
                last_character_index=c['last_character_index'])
            retrieved_sources.append(src)

        # stock and display informations about the question included the answer
        min_answer = MinimalAnswer(question_id="1", question=query,
                                   retrieved_sources=retrieved_sources,
                                   answer=answer)
        minimal_dict = min_answer.model_dump_json(indent=4)

        print(minimal_dict)

    def answer_dataset(
            self,
            student_search_results_path: str = student_search_results_path,
            save_directory: str = save_answer_dir,
            context_limite: int = 3000,
            k: int = 10) -> None:

        # check if path, k, context_limite and directory are valide
        check_path(student_search_results_path)
        check_int("context", context_limite)
        check_int("k", k)
        if not save_directory:
            raise ValueError("save_directory must have a name to be create")

        # read the document
        with open(student_search_results_path, "r", encoding="utf-8") as f:
            doc_infos = f.read()
        doc_infos = json.loads(doc_infos)

        # check and read chunks.json
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

        # find the file name to create the final json
        file_name = check_json(student_search_results_path)

        # find best_chunks for each question of the document and give it
        # to LLM to receive answers
        answer_lst = []
        get_answer = GetAnswer()
        i = 0
        for data in tqdm(doc_infos["search_results"], desc="Answer Dataset"):
            chunks = find_chunks_infos(chunks_infos, data)
            tokens = get_answer.augmente(data["question"], chunks,
                                         context_limite)
            answer = get_answer.generate(tokens)
            retrieved_sources: list[MinimalSource] = []
            for c in chunks:
                src = MinimalSource(
                    file_path=c['file_path'].strip('././'),
                    first_character_index=c['first_character_index'],
                    last_character_index=c['last_character_index'])
                retrieved_sources.append(src)
            min_answer = MinimalAnswer(question_id=data["question_id"],
                                       question=data["question"],
                                       retrieved_sources=retrieved_sources,
                                       answer=answer)
            answer_lst.append(min_answer)
            i += 1
            # save each 10 questions
            if i % 10 == 0:
                stud_search_answ = StudentSearchResultsAndAnswer(
                    search_results=answer_lst, k=k)
                create_json(save_directory, file_name, stud_search_answ)
                print(f"Saved student_search_results_and_answer to "
                      f"{save_directory}/{file_name}")

        # final save
        if answer_lst:
            stud_search_answ = StudentSearchResultsAndAnswer(
                search_results=answer_lst, k=k)
            create_json(save_directory, file_name, stud_search_answ)
            print(f"Final save : saved student_search_results_and_answer to "
                  f"{save_directory}/{file_name}")

    def evaluate(self,
                 student_search_results_path: str = my_file,
                 dataset_path: str = ref_file) -> None:
        check_path(student_search_results_path)
        check_path(dataset_path)

        evaluator(student_search_results_path, dataset_path)


def load_bm() -> Any:
    try:
        bm25 = bm25s.BM25.load("././data/processed/bm25_index",
                               load_corpus=True)
    except FileNotFoundError:
        raise FileNotFoundError("can't find index, please create it with "
                                "'uv run python -m src index'")
    return bm25


def create_json(
        save_directory: str,
        file_name: str,
        content: StudentSearchResultsAndAnswer | StudentSearchResults) -> None:
    json_content = content.model_dump_json(indent=4)
    path = Path(save_directory)
    if path.exists() is False:
        os.makedirs(save_directory)
    with open(f"{save_directory}/{file_name}", "w",
              encoding="utf-8") as f:
        f.write(json_content)


def find_chunks_infos(chunks_infos: Any, data: Any) -> list[Any]:
    save_chunk = []
    for sources in data["retrieved_sources"]:
        for c in chunks_infos:
            c_file = c['file_path'].strip("././")
            c_first = int(c['first_character_index'])
            c_last = int(c['last_character_index'])
            if c_file == sources['file_path'] \
               and c_first == int(sources['first_character_index']) \
               and c_last == int(sources['last_character_index']):
                save_chunk.append(c)
    return save_chunk
