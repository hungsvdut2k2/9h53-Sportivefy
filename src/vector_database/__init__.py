from src.vector_database.base_database import BaseDatabase


class FaissDatabase(BaseDatabase):
    def __init__(self, model_name: str) -> None:
        super().__init__(model_name)
