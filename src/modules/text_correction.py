import os
from typing import List, Optional

import numpy as np
from fuzzywuzzy import fuzz
from tqdm import tqdm


class TextCorrection:
    def __init__(self, corpus: List[str], mode="load") -> None:
        if mode == "build":
            for doc in corpus:
                if isinstance(doc["document"], list):
                    doc["document"] = "\n".join(doc["document"])
        self.corpus = corpus

    def _build_word_corpus(self, save_directory: Optional[str]):
        word_corpus = []
        for document in tqdm(self.corpus):
            content = document["document"]
            for word in content.split():
                word = word.lower()
                word = word.strip(""" !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~""")
                if word not in word_corpus:
                    word_corpus.append(word)
        with open(os.path.join(save_directory, "corpus_word.txt"), "w") as f:
            for word in word_corpus:
                f.writelines(f"{word}\n")

    def _compute_ratio(self, source: Optional[str], target: Optional[str]):
        return fuzz.ratio(source, target)

    def _correct(self, input_word: Optional[str], threshold: Optional[int]):
        ratio = np.array(
            [
                self._compute_ratio(source=input_word, target=word)
                for word in self.corpus
            ]
        )
        indices = np.argsort(ratio)[::-1]
        if ratio[indices[0]] >= threshold:
            return self.corpus[indices[0]].replace("\n", "")
