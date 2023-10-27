import uvicorn
import argparse
import faiss
from src.utils import *
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
from pydantic import BaseModel

articles_dict = read_json_file(
    file_path="/Users/viethungnguyen/9h53-Sportivefy/weights/vnexpress.json"
)

mapping_dict = read_json_file(
    file_path="/Users/viethungnguyen/9h53-Sportivefy/weights/sample.json"
)

faiss_index = faiss.read_index(
    "/Users/viethungnguyen/9h53-Sportivefy/weights/vector_db.bin"
)

model = SentenceTransformer("VoVanPhuc/sup-SimCSE-VietNamese-phobert-base")


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
            normalize_query = preprocess_text(text=query)
            embedding = model.encode(normalize_query).reshape(1, -1)
            indices = faiss_search(embedding=embedding, faiss_index=faiss_index)
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
