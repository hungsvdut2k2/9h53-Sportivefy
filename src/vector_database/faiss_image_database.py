import json
import os
from typing import Optional

import faiss
import torch
from PIL import Image
from tqdm import tqdm
from transformers import AutoImageProcessor, AutoModel

from src.vector_database.base_database import BaseDatabase
from src.vector_database.database_arguments import DatabaseArguments


class FaissImageDatabase(BaseDatabase):
    def __init__(self, args: DatabaseArguments) -> None:
        super().__init__(args=args)
        self.args = args
        self.model = AutoModel.from_pretrained(self.args.model_name)
        self.processor = AutoImageProcessor.from_pretrained(self.args.model_name)
        self.index = faiss.IndexFlatIP(self.model.config.hidden_size)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.json_content = json.load(open(self.args.json_file_path))

    def _preprocess_image(self, image_path: Optional[str]):
        image = Image.open(image_path)
        inputs = self.processor(images=image, return_tensors="pt")
        return inputs

    @torch.no_grad()
    def _get_embedding(self, image_path: Optional[str]):
        last_hidden_state = self.model(
            **self._preprocess_image(image_path=image_path)
        ).last_hidden_state
        average_pooling_result = last_hidden_state.sum(1) / last_hidden_state.size()[1]
        return average_pooling_result

    def _save(self, directory: Optional[str]):
        json_object = []
        for i in tqdm(range(len(self.json_content))):
            absolute_file_path = os.path.join(directory, self.json_content[i]["path"])
            embedding = self._get_embedding(absolute_file_path)
            self.index.add(embedding)
            json_object.append(
                {
                    "index": i,
                    "path": self.json_content[i]["path"],
                    "object_id": self.json_content[i]["object_id"],
                }
            )
        faiss.write_index(
            self.index, os.path.join(self.args.saved_file_path, "vector_database.bin")
        )
        returned_json = json.dumps(json_object).encode("utf8")
        with open(
            f"{os.path.join(self.args.saved_file_path, 'mapping.json')}",
            "w",
            encoding="utf8",
        ) as outfile:
            outfile.write(returned_json.decode())

    def _load(self, file_path: str):
        self.index = faiss.read_index(file_path)

    def _search(self, image_path: Optional[str], top_k: Optional[int]):
        embedding_query = self._get_embedding(image_path=image_path)

        d, i = self.index.search(embedding_query, k=top_k)
        return i
