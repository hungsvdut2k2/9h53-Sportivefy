import argparse
import os

from tqdm import tqdm

from src.data_augmentor.back_translation import BackTranslation
from src.utils import read_json_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", type=str, required=True)
    parser.add_argument("--file-path", type=str, required=True)
    parser.add_argument("--saved-directory", type=str, required=True)
    args = parser.parse_args()
    json_content = read_json_file(args.file_path)

    queries = [content["query"] for content in json_content]
    back_translation = BackTranslation(model_name=args.model_name)
    for i in tqdm(range(len(queries))):
        augmented_query = back_translation(text=queries[i])
        queries.append(augmented_query)

    with open(os.path.join(args.saved_directory, "in_domain.txt")) as f:
        for query in queries:
            f.writelines(f"{query}\n")
