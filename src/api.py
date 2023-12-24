import argparse
import os
import pathlib
import uuid
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from src.modules.bm25_search import BM25Search
from src.modules.text_correction import TextCorrection
from src.utils import read_json_file
from src.vector_database.database_arguments import DatabaseArguments
from src.vector_database.faiss_image_database import FaissImageDatabase
from src.vector_database.faiss_text_database import FaissTextDatabase


class App:
    def __init__(
        self,
        corpus: List[str],
        word_corpus: List[str],
        text_vector_database: FaissTextDatabase,
        image_vector_database: FaissImageDatabase,
    ) -> None:
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
        self.text_vector_database = text_vector_database
        self.image_vector_database = image_vector_database

        @self.app.get("/")
        async def root():
            return {"message": "hello"}

        @self.app.post("/text-search")
        async def text_search(query: Optional[str]):
            query = self.word_correction(query=query)
            bm25_indices = self.bm25(query=query)[:5]
            bm25_result_corpus = [self.corpus[index] for index in bm25_indices]
            indices = self.text_vector_database.search(sentence=query)
            result_corpus = [self.corpus[index] for index in indices]
            return {"result": bm25_result_corpus}

        @self.app.post("/image-search")
        async def image_search(file: UploadFile):
            file_extension = pathlib.Path(file.filename).suffix
            if file_extension.lower() not in [".jpg", ".jpeg", ".png"]:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid file format. Please upload a JPG, JPEG or PNG file.",
                )
            new_file_name = str(uuid.uuid4())
            file_location = f"./images/{new_file_name}{file_extension}"
            with open(file_location, "wb+") as file_object:
                file_object.write(file.file.read())
            distances, indices = self.image_vector_database.search(file_location)
            print(distances, indices)
            return {"indices": "success"}

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
        "--text-model-name",
        type=str,
        default="hungsvdut2k2/longformer-phobert-base-4096",
    )
    parser.add_argument("--image-model-name", type=str, default="facebook/dinov2-base")
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
    parser.add_argument(
        "--vector-database-directory",
        type=str,
        default="/Users/viethungnguyen/9h53-Sportivefy/weights",
    )
    args = parser.parse_args()
    os.makedirs("./images", exist_ok=True)
    corpus_content = read_json_file(file_path=args.corpus_file_path)
    word_corpus = open(args.word_corpus_file_path).readlines()

    text_vector_database = FaissTextDatabase(
        args=DatabaseArguments(
            {
                "model_name": args.text_model_name,
                "json_file_path": os.path.join(
                    args.vector_database_directory, "text_mapping.json"
                ),
            }
        )
    )

    image_vector_database = FaissImageDatabase(
        args=DatabaseArguments(
            {
                "model_name": args.image_model_name,
                "json_file_path": os.path.join(
                    args.vector_database_directory, "image_mapping.json"
                ),
            }
        ),
    )
    text_vector_database.load(
        os.path.join(args.vector_database_directory, "text_database.bin")
    )
    app = App(
        corpus=corpus_content,
        word_corpus=word_corpus,
        text_vector_database=text_vector_database,
        image_vector_database=image_vector_database,
    )
    app.run(port=args.port)
