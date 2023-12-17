import argparse

from src.vector_database.database_arguments import DatabaseArguments
from src.vector_database.vector_database_factory import get_vector_database

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-type", type=str, default="faiss_text")
    parser.add_argument("--json-file-path", type=str, required=True)
    parser.add_argument("--model-name", type=str, required=True)
    parser.add_argument("--saved-file-path", type=str, required=True)
    args = parser.parse_args()
    args = vars(args)

    database_type = args.pop("database_type")
    saved_file_path = args.pop("saved_file_path")
    database_arguments = DatabaseArguments(args)
    vector_database = get_vector_database(database_type=database_type, args=args)
    vector_database.save(saved_file_path)
