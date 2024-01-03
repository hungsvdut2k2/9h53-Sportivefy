import json
import os
from typing import Optional

import faiss
import torch
from tqdm import tqdm
from transformers import AutoModel, AutoTokenizer

from src.utils import preprocess_text, read_json_file
from src.vector_database.base_database import BaseDatabase
from src.vector_database.database_arguments import DatabaseArguments


class FaissTextDatabase(BaseDatabase):
    def __init__(self, args: DatabaseArguments) -> None:
        super().__init__(args=args)
        self.model = AutoModel.from_pretrained(args.model_name)
        self.index = faiss.IndexFlatIP(self.model.config.hidden_size)
        self.tokenizer = AutoTokenizer.from_pretrained(args.model_name)

    def _preprocess_json_data(self, mode="search"):
        json_data = read_json_file(self.json_file_path)
        if mode != "search":
            for i in range(len(json_data)):
                json_data[i]["document"] = preprocess_text(json_data[i]["document"])

        return json_data

    def _tokenize(self, sentence):
        return self.tokenizer(
            sentence, truncation=True, return_tensors="pt", max_length=256
        )

    @torch.no_grad()
    def _get_embedding(self, tokenized_sentences):
        return (
            torch.mean(
                self.model(**tokenized_sentences).last_hidden_state,
                dim=1,
            )
            .detach()
            .cpu()
            .numpy()
        )

    def _save(self, file_path: str):
        os.makedirs(file_path, exist_ok=True)
        json_data = self._preprocess_json_data()
        json_object = []
        for i in tqdm(range(len(json_data))):
            saved_json = {}
            object_id = json_data[i]["_id"]["$oid"]
            document = json_data[i]["document"]
            tokenized_sentences = self._tokenize(document)
            embedding = self._get_embedding(tokenized_sentences)
            self.index.add(embedding)
            saved_json["index"] = i
            saved_json["object_id"] = object_id
            json_object.append(saved_json)

        faiss.write_index(self.index, os.path.join(file_path, "vector_database.bin"))
        returned_json = json.dumps(json_object).encode("utf8")
        with open(
            f"{os.path.join(file_path, 'mapping.json')}", "w", encoding="utf8"
        ) as outfile:
            outfile.write(returned_json.decode())

    def load(self, file_path: Optional[str]):
        self.index = faiss.read_index(file_path)

    def search(self, sentence):
        tokenized_sentences = self._tokenize(sentence=sentence)
        text_embedding = self._get_embedding(tokenized_sentences=tokenized_sentences)
        distances, indices = self.index.search(text_embedding, k=200)
        json_data = self._preprocess_json_data()
        returned_json = [json_data[index]["index"] for index in indices[0]]
        return returned_json
