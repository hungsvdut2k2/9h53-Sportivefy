import g4f
import os
import json
import argparse
import pandas as pd
from loguru import logger
from g4f.Provider import (
    Bing,
)
from typing import Optional
from tqdm import tqdm


def generate_prompt(json_content: Optional[str]) -> Optional[str]:
    generated_prompt = f"##Content:{json_content}\n ##Requirements:Write a query for the content. Make sure it is in Vietnamese and must be unique for only that document,the length of answer must be suitable for a search query,the answer should be wrap up in ##Answer"
    return generated_prompt


def get_response(prompt: Optional[str]) -> Optional[str]:
    response = g4f.ChatCompletion.create(
        model=g4f.models.default,
        messages=[{"role": "user", "content": f"{prompt}"}],
        provider=Bing,
    )
    return response


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-file-path", type=str, required=True)
    parser.add_argument("--output-dir", type=str, required=True)
    parser.add_argument("--valid-file-path", type=str, default=None)
    args = parser.parse_args()
    dataframe = pd.DataFrame()
    json_content = json.load(open(args.json_file_path))
    if args.valid_file_path:
        dataframe = pd.read_csv(args.valid_file_path)
        indices = pd.read_csv(args.valid_file_path)["index"].tolist()
        logger.info("Start Remove Stuff")
        for index in tqdm(sorted(indices, reverse=True)):
            json_content.pop(index)
    dataframe_length = len(dataframe)
    logger.info("Start Generate Query")
    for i in tqdm(range(len(json_content))):
        try:
            new_row = {}
            generated_prompt = generate_prompt(json_content=json_content[i]["article"])
            response = get_response(generate_prompt(generated_prompt))
            new_row["object_id"] = json_content[i]["_id"]["$oid"]
            new_row["query"] = response
            new_row["index"] = dataframe_length + i
            dataframe = dataframe._append(new_row, ignore_index=True)
        except KeyboardInterrupt:
            dataframe.to_csv(os.path.join(args.output_dir, "query.csv"), index=False)
            break
        except:
            dataframe_length += 1
            logger.debug(f"Error at index {i}")
    dataframe.to_csv(os.path.join(args.output_dir, "query.csv"), index=False)
