    # quand tout est chunk on appelle la fonction qui utilise bm25
    # avec en parametre la liste de tous les chunks

    # parallelement sauvegarder les chunks a cote dans un JSON par exemple,
    # avec le texte, le fichier source, les positions de debut et de fin
    # pour retrouver le chunk 42 par exemple
    # retriever.save("data/processed/bm25_index")
    # # + ton propre fichier chunks.json
    # # à la recherche :
    # results, scores = retriever.retrieve(q_tokens, k=k)   # results = indices
    # best = [chunks[i] for i in results[0]]

from src.utils.display import print_success
from pathlib import Path
import os
import zipfile
from chonkie import CodeChunker

class Chunker:

    def check_zip(self) -> None:
        path_to_folder = "././data/raw/"
        path = Path(path_to_folder)
        if path.exists() is False:
            raise ValueError("path to folder invalid")
        if path.is_dir() is False:
            raise ValueError("this is not a directory")

        file = "././data/raw/vllm-0.10.1.zip"
        file_path = Path(file)
        if file_path.exists is False:
            raise ValueError("can't find vllm-0.10.1.zip")
        if file_path.is_file() is False:
            raise ValueError("this is not a file")
        if not os.access(file_path, os.R_OK):
            raise ValueError("can't read the file, please change permissions")
        if not os.access(file_path, os.X_OK):
            raise ValueError("can't execute the file, please change permissions")


    def extract_zip(self) -> list[str] | None:
        file_list = []
        try:
            with zipfile.ZipFile("././data/raw/vllm-0.10.1.zip", "r") as z:
                z.extractall(path="././data/raw/")
                print_success("All files has been extracted")
                for info in z.infolist():
                    file_list.append(f"././data/raw/{info.filename}")
                return file_list
        except FileNotFoundError:
            raise ValueError("can't find files")

    def chunk_code_file(self, max_chunk_size: int,
                        file: str) -> list[dict] | None:
        check_file = Path(file)
        if check_file.exists is False:
            raise ValueError(f"can't find {file}")
        if not os.access(check_file, os.R_OK):
            raise ValueError(f"can't read {file}, please change permissions")

        with open(file, "r", encoding="utf-8") as f:
            code_source = f.read()

        chunker = CodeChunker(language="python",
                              chunk_size=max_chunk_size)

        chunks_txt = [chunk.text for chunk in chunker.chunk(code_source)]
        i = 0
        chunks = []
        for txt in chunks_txt:
            if i != 0:
                i += 1
            chunk = {}
            chunk["text"] = txt
            chunk["file_path"] = file
            chunk["first_character_index"] = i
            i += max_chunk_size
            chunk["last_character_index"] = i
            chunks.append(chunk)

        return chunks

    def chunk_docs_file(self, max_chunk_size: int, file: str) -> str:
        # utiliser RecursiveChunker et OverlapRefinery
        pass

    def save_chunk(self, chunk: str) -> None:
        # créer un JSON avec tous les chunks : le texte, le fichier source, les
        # positions de début et de fin
        # mettre un attribut directement à la classe pour enregistrer le contenu
        # du json au cas où celui-ci est supprimé aussi
        pass
