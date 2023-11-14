import json
import numpy as np
from pyvi.ViTokenizer import tokenize


def read_json_file(file_path: str) -> dict:
    return json.load(open(file_path))


def normalize_text(text: str) -> str:
    text = text.lower()
    text = text.strip(""" !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~""")
    text = text.replace("\n", " ")
    return text


def segment(text: str) -> str:
    return tokenize(text)


def preprocess_text(text: str) -> str:
    text = normalize_text(text)
    text = segment(text)
    return text


def faiss_search(embedding: np.ndarray, faiss_index):
    d, i = faiss_index.search(embedding, 100)
    return i[0]


def mapping_value(indices: list, mapping_dict: dict) -> list:
    object_id = [
        mapping_value["object_id"]
        for mapping_value in mapping_dict
        if int(mapping_value["index"]) in indices
    ]
    return object_id


def get_articles(object_id: list, articles_dict: dict) -> list:
    articles = [
        article for article in articles_dict if article["_id"]["$oid"] in object_id
    ]

    return articles