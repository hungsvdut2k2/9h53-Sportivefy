import argparse
import json
import os
from typing import Optional

import g4f
import pandas as pd
from g4f.Provider import Bing
from loguru import logger
from tqdm import tqdm


def generate_prompt() -> Optional[str]:
    generated_prompt = "##Role: Search Engine\n ##Objective: Generate 30 sport queries with flexible length in Vietnamese, the content must be as creative as possible\n ##Content: About Sport and must have one famous athlete's name in one query"
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
    parser.add_argument("--output-dir", type=str, required=True)
    parser.add_argument("--num-request", type=int, default=None)
    args = parser.parse_args()
    dataframe = pd.DataFrame()
    dataframe_length = len(dataframe)
    logger.info("Start Generate Query")
    for i in tqdm(range(args.num_request)):
        length = (
            len(os.listdir("/Users/viethungnguyen/9h53-Sportivefy/dataset/domain")) - 1
        )
        try:
            prompt = generate_prompt()
            response = get_response(prompt=prompt)
            with open(os.path.join(args.output_dir, f"{length + i + 5}.txt"), "w") as f:
                f.writelines(response)
        except Exception as e:
            dataframe_length += 1
            logger.debug(f"Error {e} at index {i}")
