class RAGEngine():

    def index(self, max_chunk_size: int = 2000) -> None:
        # chunk tout data/raw/ et crée un index dans data/processed
        # etape 1 : check que le max_chunk_size est valide
        # etape 2 : appeler une fonction qui chunk avec chonkie en donnant en
        # parametres la max_chunk_size
        if isinstance(max_chunk_size, bool):
            raise TypeError("max_chunk_size must be an integer")
        try:
            max_chunk_size = int(max_chunk_size)
        except (TypeError, ValueError):
            raise TypeError("max_chunk_size must be an integer")
        if max_chunk_size <= 0:
            raise ValueError("max_chunk_size must be positive")
        if max_chunk_size > 2000:
            raise ValueError("max_chunk_size can't be more than 2000")

    def search(self, query: str = "", k: int = 10,
               verbose: bool = True) -> None:
        # retourne les meilleurs chunks pour une question
        print(query)
        if isinstance(query, bool) or isinstance(query, int)\
           or isinstance(query, float):
            raise TypeError("query must be a string")
        if not query or query == 'query':
            raise ValueError("query must be a question")
        return "THIS IS SEARCH"

    def search_dataset(self, dataset_path: str = "", k: int = 10,
                       save_directory: str = "") -> None:
        # lance la recherche dans un jeu de données et écrit un JSON
        # StudentSearchResults
        return "THIS IS SEARCH DATASET"

    def answer(self, query: str = "", k: int = 10,
               context_limit: int = 3000) -> None:
        # répond a une question en utilisant le retrieved context
        return "THIS IS ANSWER"

    def answer_dataset(self, student_search_results_path: str = "",
                       save_directory: str = "",
                       context_limit: int = 3000) -> None:
        # génère les réponses pour un jeu de données en produisant un JSON
        # StudentSearchResultsAndAnswer
        return "THIS IS ANSWER DATASET"

    def evaluate(self, student_search_results_path: str = "",
                 dataset_path: str = "") -> None:
        # cela rapporte mon propre recall@k par rapport à un jeu de données de
        # référence pour mes propres tests
        return "THIS IS EVALUATE"
