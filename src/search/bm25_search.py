import numpy as np
from rank_bm25 import BM25Okapi
from typing import Optional, List


class BM25Search:
    def __init__(self, corpus: Optional[List]) -> None:
        for doc in corpus:
            if isinstance(doc["article"], list):
                doc["article"] = "\n".join(doc["article"])
        new_corpus = [doc["article"].lower() for doc in corpus]
        tokenized_corpus = [doc.split(" ") for doc in new_corpus]

        self.bm25 = BM25Okapi(tokenized_corpus)

    def __call__(self, query: Optional[str]):
        tokenized_query = query.split(" ")
        doc_scores = self.bm25.get_scores(tokenized_query)
        indices = np.argsort(doc_scores)[::-1]

        return indices
