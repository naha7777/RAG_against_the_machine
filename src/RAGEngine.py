from src.indexer.index import indexer
from src.retriever.retrieving import retriever


class RAGEngine:

    def index(self, max_chunk_size: int = 2000) -> None:
        # check if max_chunk_size is valide and call indexer function
        if isinstance(max_chunk_size, bool):
            raise TypeError("max_chunk_size must be an integer")

        check_int("max_chunk_size", max_chunk_size)

        indexer(max_chunk_size)

    def search(self, query: str = "", k: int = 10) -> None:
        # check if query and k are valide and call retriever function
        if isinstance(query, (bool, int, float, list, dict)):
            raise TypeError("query must be a string")
        if not query or query == 'query':
            raise ValueError("query must be a question")

        check_int("k", k)

        retriever(query, k)

    def search_dataset(self, dataset_path: str = "", k: int = 10,
                       save_directory: str = "") -> None:
        # lance la recherche dans un jeu de données et écrit un JSON
        # StudentSearchResults
        check_int("k", k)

    def answer(self, query: str = "", k: int = 10,
               context_limit: int = 3000) -> None:
        # répond a une question en utilisant le retrieved context
        check_int("k", k)

    def answer_dataset(self, student_search_results_path: str = "",
                       save_directory: str = "",
                       context_limit: int = 3000) -> None:
        # génère les réponses pour un jeu de données en produisant un JSON
        # StudentSearchResultsAndAnswer
        pass

    def evaluate(self, student_search_results_path: str = "",
                 dataset_path: str = "") -> None:
        # cela rapporte mon propre recall@k par rapport à un jeu de données de
        # référence pour mes propres tests
        pass


def check_int(name: str, number: int):
    if isinstance(number, bool):
        raise TypeError(f"{name} must be an integer")
    try:
        number = int(number)
    except (TypeError, ValueError):
        raise TypeError(f"{name} must be an integer")
    if number <= 0:
        raise ValueError(f"{name} must be positive")
    if number > 500 and name == "k":
        raise ValueError(f"{name} can't be more than 500, this is too much")
    if number > 2000 and name == "max_chunk_size":
        raise ValueError(f"{name} can't be more than 2000, this is too much")
