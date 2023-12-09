import uvicorn
import argparse
from src.utils import read_json_file
from src.search.bm25_search import BM25Search
from typing import Optional, List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


class App:
    def __init__(self, corpus: Optional[List]) -> None:
        self.app = FastAPI()
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.corpus = corpus
        self.bm25 = BM25Search(corpus=corpus)

        @self.app.get("/")
        async def root():
            return {"message": "hello"}

        @self.app.get("/text-search")
        async def text_search(query: str):
            indices = self.bm25(query=query)[:100]
            result_corpus = [self.corpus[index] for index in indices]
            return result_corpus

    def run(self, port: int):
        uvicorn.run(self.app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument(
        "--corpus-file-path",
        type=str,
        default="/Users/viethungnguyen/9h53-Sportivefy/weights/corpus_final.json",
    )
    args = parser.parse_args()
    corpus_content = read_json_file(file_path=args.corpus_file_path)

    app = App(corpus=corpus_content)
    app.run(port=args.port)
