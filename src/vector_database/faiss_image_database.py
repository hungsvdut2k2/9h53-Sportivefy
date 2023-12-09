import faiss
import os
import json
import torch
import clip
from typing import Optional
from loguru import logger
from tqdm import tqdm
from PIL import Image
from src.vector_database.base_database import BaseDatabase
from src.vector_database.database_arguments import DatabaseArguments


class FaissTextDatabase(BaseDatabase):
    def __init__(self, args: DatabaseArguments) -> None:
        super().__init__(args=args)
        self.index = faiss.IndexFlatIP(self.model.config.hidden_size)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, self.preprocess = clip.load(
            self.args.model_name, device=self.device
        )

    def _preprocess_image(self, image_path: Optional[str]):
        image = self.preprocess(Image.open(image_path)).unsqueeze(0).to(self.device)
        return image

    @torch.no_grad()
    def _get_embedding(self, image_path: Optional[str]):
        image_features = self.model.encode_image(
            self._preprocess_image(image_path=image_path)
        )
        return image_features

    def _save(self, file_path: Optional[str]):
        file_paths = os.listdir(self.args.directory)
        json_object = []
        for i in tqdm(range(file_paths)):
            absolute_file_path = os.path.join(self.args.directory, file_paths[i])
            embedding = (
                self._get_embedding(absolute_file_path)
                .detach()
                .cpu()
                .numpy()
                .reshape(-1, 768)
            )
            self.index.add(embedding)
            json_object.append({"index": i, "file_path": file_path[i]})

        faiss.write_index(self.index, os.path.join(file_path, "vector_database.bin"))
        returned_json = json.dumps(json_object).encode("utf8")
        with open(
            f"{os.path.join(file_path, 'mapping.json')}", "w", encoding="utf8"
        ) as outfile:
            outfile.write(returned_json.decode())

    def _load(self, file_path: str):
        self.index = faiss.read_index(file_path)

    def _search(self, image_path: Optional[str], top_k: Optional[int]):
        embedding_query = self._get_embedding(image_path=image_path)

        d, i = self.index.search(embedding_query, k=top_k)
        return i
