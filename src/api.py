import uvicorn
import argparse
from src.utils import read_json_file
from src.modules.bm25_search import BM25Search
from src.modules.text_correction import TextCorrection
from typing import Optional, List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


class App:
    def __init__(self, corpus: List[str], word_corpus: List[str]) -> None:
        self.app = FastAPI()
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.corpus = corpus
        self.word_corpus = word_corpus
        self.text_correction = TextCorrection(corpus=word_corpus)
        self.bm25 = BM25Search(corpus=corpus)

        @self.app.get("/")
        async def root():
            return {"message": "hello"}

        @self.app.get("/text-search")
        async def text_search(query: str):
            query = self.word_correction(query=query)
            indices = self.bm25(query=query)[:5]
            result_corpus = [self.corpus[index] for index in indices]
            return result_corpus

    def word_correction(self, query: Optional[str]):
        query = query.lower()
        query = query.split()
        for i in range(len(query)):
            if query[i] not in self.word_corpus:
                corrected_word = self.text_correction._correct(
                    input_word=query[i], threshold=60
                )
                if corrected_word:
                    query[i] = corrected_word
        query = " ".join(query)
        return query

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
    parser.add_argument(
        "--word-corpus-file-path",
        type=str,
        default="/Users/viethungnguyen/9h53-Sportivefy/weights/corpus_word.txt",
    )
    args = parser.parse_args()
    corpus_content = read_json_file(file_path=args.corpus_file_path)
    word_corpus = open(args.word_corpus_file_path).readlines()

    app = App(corpus=corpus_content, word_corpus=word_corpus)
    app.run(port=args.port)
