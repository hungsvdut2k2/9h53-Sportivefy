import json
import os

import faiss
import torch
from tqdm import tqdm

from src.utils import preprocess_text, read_json_file
from src.vector_database.base_database import BaseDatabase
from src.vector_database.database_arguments import DatabaseArguments


class FaissTextDatabase(BaseDatabase):
    def __init__(self, args: DatabaseArguments) -> None:
        super().__init__(args=args)
        self.index = faiss.IndexFlatIP(self.model.config.hidden_size)

    def _preprocess_json_data(self):
        json_data = read_json_file(self.json_file_path)
        for i in range(len(json_data)):
            json_data[i]["article"] = preprocess_text(json_data[i]["article"])

        return json_data

    def _tokenize(self, sentence):
        return self.tokenizer(
            sentence, padding=True, truncation=True, return_tensors="pt"
        )

    @torch.no_grad()
    def _get_embedding(self, tokenized_sentences):
        return self.model(
            **tokenized_sentences, output_hidden_states=True, return_dict=True
        ).pooler_output

    def _save(self, file_path: str):
        os.makedirs(file_path, exist_ok=True)
        json_data = self._preprocess_json_data()
        json_object = []
        for i in tqdm(range(len(json_data))):
            saved_json = {}
            object_id = json_data[i]["_id"]["$oid"]
            article = json_data[i]["article"]
            tokenized_sentences = self._tokenize(article)
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

    def _load(self, file_path: str):
        self.index = faiss.read_index(file_path)

    def _search(self, query: str, top_k: int):
        tokenized_query = self._tokenize(query)
        embedding_query = self._get_embedding(tokenized_query)

        d, i = self.index.search(embedding_query, k=top_k)
        return i
