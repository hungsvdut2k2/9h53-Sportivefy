import argparse
import unicodedata
import re
import os
import pathlib
import uuid
import shutil

import requests
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from transformers import (
    AutoModelForCausalLM,
    AutoModelForSequenceClassification,
    AutoTokenizer,
    pipeline,
)

from src.modules.bm25_search import BM25Search
from src.modules.text_correction import TextCorrection
from src.utils import preprocess_text, read_json_file
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
        auto_casual_model_name: Optional[str],
        domain_classification_model_name: Optional[str],
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
        self.auto_casual_model = AutoModelForCausalLM.from_pretrained(
            auto_casual_model_name
        )
        self.auto_casual_tokenizer = AutoTokenizer.from_pretrained(
            auto_casual_model_name
        )
        self.domain_pipeline = pipeline(
            "sentiment-analysis",
            model=AutoModelForSequenceClassification.from_pretrained(
                domain_classification_model_name
            ),
            tokenizer=AutoTokenizer.from_pretrained(domain_classification_model_name),
            device="cpu",
        )

        @self.app.get("/")
        async def root():
            return {"message": "hello"}

        @self.app.get("/text-search")
        async def text_search(query: Optional[str]):
            query = self.word_correction(query=query)
            query = preprocess_text(query)
            preds = self.domain_pipeline(query)
            if preds[0]["label"] == "out_of_domain":
                return {
                    "response": "your query does not seem to be related to sports content."
                }
            #bm25_indices = self.bm25(query=query)[:200]
            indices = self.text_vector_database.search(query)
            result_corpus = [self.corpus[index]["title"] for index in indices]
            result_corpus = list(dict.fromkeys(result_corpus))
            return {"response": result_corpus}

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
            titles = self.image_vector_database.search(file_location)
            # result_title = [self.get_slug(title) for title in titles]
            result_title = list(dict.fromkeys(titles))
            return {"response": result_title}

        @self.app.post("/document-generation")
        async def document_generate(prompt: Optional[str]):
            inputs = self.auto_casual_tokenizer(prompt, return_tensors="pt")
            outputs = self.auto_casual_model.generate(
                **inputs,
                max_new_tokens=100,
                do_sample=True,
                top_k=5,
                top_p=0.95,
                temperature=0.5,
                eos_token_id=self.auto_casual_model.config.eos_token_id,
                pad_token_id=self.auto_casual_model.config.eos_token_id,
            )
            generated_content = self.auto_casual_tokenizer.batch_decode(
                outputs, skip_special_tokens=True
            )[0]
            return {"response": generated_content}
    
        @self.app.post("/add-article")
        async def add_article(title: Optional[str], content: Optional[str], image_url: Optional[str]):
            object_id = str(uuid.uuid4())
            new_file_path = os.path.join("./images", f"{object_id}.jpg")

            #save images
            response = requests.get(image_url, stream=True)
            with open(new_file_path, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            
            self.image_vector_database.add_image(new_file_path, title, object_id)

            #save text

            sentence = title + "." + content
            self.text_vector_database.add(sentence)
            self.corpus.append({"_id": {"$oid" : object_id}, "title": title})
            print(self.corpus[-1])

            return {"response": "ok"}


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

    def get_slug(self, string, separator=""):
        # Remove text within parentheses and trim
        string = re.sub(r"\([^)]*\)", "", string).strip()

        # Convert to lowercase
        string = string.lower()

        # Remove periods
        string = string.replace(".", "")

        # Normalize Unicode characters to decompose accents
        string = unicodedata.normalize("NFD", string).encode("ascii", "ignore").decode()

        # Replace đ and Đ with d
        string = string.replace("đ", "d").replace("Đ", "d")

        # Remove characters that are not alphanumeric, spaces, or hyphens
        string = re.sub(r"[^0-9a-z-\s]", "", string)

        # Replace spaces with hyphens
        string = string.replace(" ", "-")

        # Collapse multiple hyphens into a single one
        string = re.sub(r"-+", "-", string)

        # Remove leading and trailing hyphens
        string = string.strip("-")

        # Join with no separator
        return separator.join(string.split("-"))

    def run(self, port: int):
        uvicorn.run(self.app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument(
        "--text-model-name",
        type=str,
        default="hungsvdut2k2/longformer-phobert-base-256",
    )
    parser.add_argument("--image-model-name", type=str, default="facebook/dinov2-base")
    parser.add_argument(
        "--text-generation-model-name",
        type=str,
        default="hungsvdut2k2/news-article-generator",
    )
    parser.add_argument(
        "--domain-classification-model-name",
        type=str,
        default="hungsvdut2k2/sport-domain-classification",
    )
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
    image_vector_database.load(
        os.path.join(args.vector_database_directory, "image_database.bin")
    )
    app = App(
        corpus=corpus_content,
        word_corpus=word_corpus,
        text_vector_database=text_vector_database,
        image_vector_database=image_vector_database,
        auto_casual_model_name=args.text_generation_model_name,
        domain_classification_model_name=args.domain_classification_model_name,
    )
    app.run(port=args.port)
