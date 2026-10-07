from pathlib import Path
import os


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


def check_query(query:str) -> None:
    if isinstance(query, (bool, int, float, list, dict)):
        raise TypeError("query must be a string")
    if not query or query == 'query':
        raise ValueError("query must be a question")


def check_json(path: str) -> str:
    if "/" in path:
        cut_path = path.split("/")
        file_name = cut_path[len(cut_path) - 1]
    else:
        file_name = path
    if not file_name.endswith(".json"):
        raise ValueError("student_search_results_path must go to a json"
                         " file")
    return file_name


def check_path(path: str) -> None:
    path = Path(path)
    if path.exists() is False:
        raise ValueError("can't find the file")
    if path.is_file() is False:
        raise ValueError("this is not a file")
    if not os.access(path, os.R_OK):
        raise ValueError("can't read the file, please change permissions")
