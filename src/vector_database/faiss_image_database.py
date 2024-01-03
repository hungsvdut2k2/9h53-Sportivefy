import json
import os
from typing import Optional
import open_clip
import faiss
import numpy as np
import pandas as pd
import torch
from PIL import Image
from tqdm import tqdm
from transformers import AutoImageProcessor, AutoModel

from src.vector_database.base_database import BaseDatabase
from src.vector_database.database_arguments import DatabaseArguments


class FaissImageDatabase(BaseDatabase):
    def __init__(self, args: DatabaseArguments) -> None:
        self.args = args
        self.json_content = json.load(open(self.args.json_file_path))
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            "ViT-B-32", pretrained="laion2b_s34b_b79k"
        )
        self.index = faiss.IndexFlatIP(512)

    def _preprocess_image(self, image_path: Optional[str]):
        image = self.preprocess(Image.open(image_path)).unsqueeze(0)
        return image

    @torch.no_grad()
    def _get_embedding(self, image_path: Optional[str]):
        last_hidden_state = self.model.encode_image(self._preprocess_image(image_path))
        return last_hidden_state.detach().cpu().numpy()

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

    def load(self, file_path: Optional[str]):
        self.index = faiss.read_index(file_path)

    def search(self, image_path: Optional[str]):
        image_embedding = self._get_embedding(image_path=image_path)
        distances, indices = self.index.search(image_embedding, k=200)
        mapping_list = [self.json_content[index] for index in indices[0]]
        mapping_df = pd.DataFrame(mapping_list)
        mapping_df.drop_duplicates(subset=["object_id"], inplace=True)
        titles = mapping_df["title"].tolist()
        titles = [title for title in titles if isinstance(title, str)]
        return titles
