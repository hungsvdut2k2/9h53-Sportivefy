import uvicorn
import argparse
from src.utils import *
from src.vector_database.vector_database_factory import get_vector_database
from src.vector_database.database_arguments import DatabaseArguments
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

database_arguments = DatabaseArguments(
    {
        "model_name": "hungsvdut2k2/vietnamese-xlm-roberta",
        "json_file_path": "/Users/viethungnguyen/9h53-Sportivefy/weights/vnexpress.json",
    }
)
vector_database = get_vector_database(database_type="faiss", args=database_arguments)
vector_database.load(
    file_path="/Users/viethungnguyen/9h53-Sportivefy/weights/vector_database.bin"
)


articles_dict = read_json_file(
    file_path="/Users/viethungnguyen/9h53-Sportivefy/weights/vnexpress.json"
)

mapping_dict = read_json_file(
    file_path="/Users/viethungnguyen/9h53-Sportivefy/weights/mapping.json"
)


class App:
    def __init__(self) -> None:
        self.app = FastAPI()
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @self.app.get("/")
        async def root():
            return {"message": "hello"}

        @self.app.get("/text-search")
        async def text_search(query: str):
            normalize_query = preprocess_text(dataset=query)
            indices = vector_database.search(query=normalize_query, top_k=100)
            object_id = mapping_value(indices=indices, mapping_dict=mapping_dict)
            articles = get_articles(object_id=object_id, articles_dict=articles_dict)
            return articles

    def run(self, port: int):
        uvicorn.run(self.app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    app = App()
    app.run(port=args.port)
