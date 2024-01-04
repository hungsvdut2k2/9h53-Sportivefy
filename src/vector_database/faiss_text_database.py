import json
import os
import numpy as np
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
        self.json_data = self._preprocess_json_data()

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

    def cosine_similarity(self, vector, matrix):
        """
        Calculate the cosine similarity between a vector and each row of a matrix.

        :param vector: A 1D NumPy array.
        :param matrix: A 2D NumPy array with the same number of columns as the vector.
        :return: A 1D NumPy array containing the cosine similarity between the vector and each row of the matrix.
        """
        # Normalize the vector
        vector_norm = vector / np.linalg.norm(vector)
        
        # Normalize each row in the matrix
        matrix_norm = matrix / np.linalg.norm(matrix, axis=1, keepdims=True)
        
        # Calculate the cosine similarity
        return np.dot(vector_norm, matrix_norm.T)

    def search(self, sentence):
        tokenized_sentences = self._tokenize(sentence=sentence)
        text_embedding = self._get_embedding(tokenized_sentences=tokenized_sentences)
        distances, indices = self.index.search(text_embedding, k=200)
        return indices[0]
    
    def temp_search(self, query,indices):
        reconstructed_vectors = np.array([self.index.reconstruct(int(idx)) for idx in indices])
        tokenized_sentences = self._tokenize(sentence=query)
        text_embedding = self._get_embedding(tokenized_sentences=tokenized_sentences)
        cosine_similarities = self.cosine_similarity(text_embedding, reconstructed_vectors)[0]
        output_indices = np.argsort(cosine_similarities)[::-1]
        final_indices = [indices[output_indices[i]] for i in range(len(output_indices))]
        return final_indices

    def add(self, sentence):
        tokenized_sentences = self._tokenize(sentence=sentence)
        text_embedding = self._get_embedding(tokenized_sentences=tokenized_sentences)
        self.index.add(text_embedding) 
        print(self.index.ntotal)