import argparse

from src.modules.text_correction import TextCorrection
from src.utils import read_json_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file-path",
        type=str,
        default="/Users/viethungnguyen/9h53-Sportivefy/weights/corpus_final.json",
    )
    parser.add_argument(
        "--save-directory",
        type=str,
        default="/Users/viethungnguyen/9h53-Sportivefy/weights",
    )
    args = parser.parse_args()
    corpus = read_json_file(file_path=args.file_path)
    correction = TextCorrection(corpus=corpus, mode="build")
    correction._build_word_corpus(save_directory=args.save_directory)
