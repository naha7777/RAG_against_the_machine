from src.indexer.index import indexer
from src.retriever.retrieving import retriever
from src.answering.answer import GetAnswer
from src.models import (MinimalSearchResults, StudentSearchResults,
                        MinimalAnswer, MinimalSource,
                        StudentSearchResultsAndAnswer)
from pathlib import Path
from typing import Any
import os
import json


dataset_path = "data/datasets/public/UnansweredQuestions/"\
               "dataset_docs_public.json"
save_directory = "data/output/search_results/UnansweredQuestions"
student_search_results_path = "data/output/search_results/"\
                              "UnansweredQuestions/dataset_docs_public.json"
save_answer_dir = "data/output/search_results_and_answer/UnansweredQuestions"


class RAGEngine:

    def index(self, max_chunk_size: int = 2000) -> None:
        # check if max_chunk_size is valide and call indexer function
        if isinstance(max_chunk_size, bool):
            raise TypeError("max_chunk_size must be an integer")

        check_int("max_chunk_size", max_chunk_size)

        indexer(max_chunk_size)

    def search(self, query: str = "", k: int = 10,
               verbose: bool = True) -> None:
        # check if query and k are valide
        if isinstance(query, (bool, int, float, list, dict)):
            raise TypeError("query must be a string")
        if not query or query == 'query':
            raise ValueError("query must be a question")

        check_int("k", k)

        # call retriever function
        retrieved_sources = retriever(query, k, True)

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
        #  check if path, k, and directory are valide
        path = Path(dataset_path)
        if path.exists() is False:
            raise ValueError("can't find the file")
        if path.is_file() is False:
            raise ValueError("this is not a file")
        if not os.access(path, os.R_OK):
            raise ValueError("can't read the file, please change permissions")
        check_int("k", k)
        if not save_directory:
            raise ValueError("save_directory must have a name to be create")

        # read the dataset document
        with open(dataset_path, "r", encoding="utf-8") as f:
            datasets_info = f.read()
        datasets_info = json.loads(datasets_info)

        search_res_list = []
        # call the retriever for each question on dataset and stock it
        # on MinimalSearchResults model
        for data in datasets_info["rag_questions"]:
            retrieved_sources = retriever(data["question"], k, True)
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
        if isinstance(query, (bool, int, float, list, dict)):
            raise TypeError("query must be a string")
        if not query or query == 'query':
            raise ValueError("query must be a question")
        check_int("k", k)
        check_int("context", context_limite)

        # call retriever function
        best_chunks: list[Any] = retriever(query, k, False)

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
        path = Path(student_search_results_path)
        if path.exists() is False:
            raise ValueError("can't find the file with the path :"
                             f" {student_search_results_path}")
        if path.is_file() is False:
            raise ValueError("this is not a file")
        if not os.access(path, os.R_OK):
            raise ValueError("can't read the file, please change permissions")
        check_int("context", context_limite)
        check_int("k", k)
        if not save_directory:
            raise ValueError("save_directory must have a name to be create")

        # read the document
        with open(student_search_results_path, "r", encoding="utf-8") as f:
            doc_infos = f.read()
        doc_infos = json.loads(doc_infos)

        # find best_chunks for each question of the document and give it
        # to LLM to receive answers
        answer_lst = []
        for data in doc_infos["rag_questions"]:
            best_chunks = retriever(data["question"], k, False)
            get_answer = GetAnswer()
            tokens = get_answer.augmente(data["question"], best_chunks,
                                         context_limite)
            answer = get_answer.generate(tokens)
            retrieved_sources: list[MinimalSource] = []
            for c in best_chunks:
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

        stud_search_answ = StudentSearchResultsAndAnswer(
            search_results=answer_lst,
            k=k
            )

        # find the file name to create the final json
        file_name = check_json(student_search_results_path)

        # json creation
        create_json(save_directory, file_name, stud_search_answ)
        print(f"Saved student_search_results_and_answer to {save_directory}"
              f"/{file_name}")

    def evaluate(self,
                 student_search_results_path: str = "",
                 dataset_path: str = "") -> None:
        # cela rapporte mon propre recall@k par rapport à un jeu de données de
        # référence pour mes propres tests
        pass


def check_int(name: str, number: int) -> None:
    if isinstance(number, bool):
        raise TypeError(f"{name} must be an integer")
    try:
        number = int(number)
    except (TypeError, ValueError):
        raise TypeError(f"{name} must be an integer")
    if number <= 0:
        raise ValueError(f"{name} must be positive")
    if number > 20 and name == "k":
        raise ValueError(f"{name} can't be more than 500, this is too much")
    if number > 2000 and name == "max_chunk_size":
        raise ValueError(f"{name} can't be more than 2000, this is too much")
    if number > 8000 and name == "context":
        raise ValueError(f"{name} can't be more than 8000, this is too much")

def check_json(path: str) -> str:
    if "/" in path:
        cut_path = path.split("/")
        file_name = cut_path[len(cut_path) - 1]
    else:
        file_name = path
    if not file_name.endswith(".json"):
        raise ValueError("student_search_results_path must go to a json"
                         " file")

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
