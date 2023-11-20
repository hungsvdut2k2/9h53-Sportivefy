from abc import abstractmethod
from transformers import AutoModel, AutoTokenizer
from src.vector_database.database_arguments import DatabaseArguments


class BaseDatabase:
    def __init__(self, args: DatabaseArguments) -> None:
        self.model = AutoModel.from_pretrained(args["model_name"])
        self.tokenizer = AutoTokenizer.from_pretrained(args["model_name"])
        self.json_file_path = args["json_file_path"]

    def save(self, file_path: str):
        self._save(file_path)

    @abstractmethod
    def _save(self, file_path: str):
        pass

    def load(self, file_path: str):
        self._load(file_path)

    @abstractmethod
    def _load(self, file_path: str):
        pass

    def search(self, query: str, top_k: int):
        return self._search(query, top_k)

    @abstractmethod
    def _search(self, query: str, top_k: int):
        pass