from src.vector_database.base_database import BaseDatabase
from vector_database.faiss_text_database import FaissTextDatabase
from src.vector_database.database_arguments import DatabaseArguments


def get_vector_database(database_type: str, args: DatabaseArguments) -> BaseDatabase:
    database_dict = {"faiss_text": FaissTextDatabase(args)}
    if database_type in database_dict.keys():
        return database_dict[database_type]
    raise ValueError("Unsupported Vector Database")
