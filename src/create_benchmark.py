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
    generated_prompt = "##Vai trò: chuyên gia văn học Việt Nam \n ##Mục tiêu: Sinh ra 30 câu hỏi liên quan đến chủ đề văn học mà tôi cung cấp, các câu cần nằm sau ##Answer, các câu hỏi cần có sự sáng tạo về nội dung và pattern không được trùng lặp \n ## Chủ đề: Câu hỏi về phép liên kết, nối câu\n ##Mô tả: Câu hỏi về phép liên kết nối câu\n ##Lưu ý: Tôi chỉ cần câu hỏi và không cần câu trả lời"
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
        length = len(os.listdir("/Users/viethungnguyen/question-type-data/lket_cau"))
        try:
            prompt = generate_prompt()
            response = get_response(prompt=prompt)
            with open(os.path.join(args.output_dir, f"{length + i + 5}.txt"), "w") as f:
                f.writelines(response)
        except Exception as e:
            dataframe_length += 1
            logger.debug(f"Error {e} at index {i}")
