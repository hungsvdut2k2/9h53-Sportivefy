import os
import argparse
import pandas as pd
import multiprocessing as mp
import logging
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from tqdm import tqdm

logger = logging.getLogger(__name__)


def get_collection(connection_string: str):
    client = MongoClient(connection_string, server_api=ServerApi("1"))
    database = client["articles"]
    collection = database["vnexpress"]
    return collection


load_dotenv()
connection_string = os.getenv("CONNECTION_STRING")
collection = get_collection(connection_string)


def translate_sport(sport: str) -> str:
    english_sport = {
        "bóng đá": "football",
        "tennis": "tennis",
        "marathon": "marathon",
        "đua xe": "racing",
        "golf": "golf",
        "cờ vua": "chess",
        "điền kinh": "track-and-field",
        "hậu trường": "behind-the-scences",
    }

    return english_sport[sport] if sport in english_sport.keys() else "other"


def get_articles(url: str):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            result = {}
            articles = []
            soup = BeautifulSoup(response.text, "html.parser")
            bread_crumb = soup.find("ul", {"class": "breadcrumb"})

            first_menu_title = bread_crumb.find_all("li")[0].text.lower()

            if first_menu_title == "thể thao":
                # get sport type
                second_menu_title = bread_crumb.find_all("li")[1].text.lower()
                if second_menu_title != "các môn khác":
                    sport_type = second_menu_title
                else:
                    if len(bread_crumb.find_all("li")) < 2:
                        sport_type = "other"
                    else:
                        sport_type = bread_crumb.find_all("li")[2].text.lower()

                # get title
                title = soup.find("h1", {"class": "title-detail"}).text
                # get articles

                article_tags = soup.find_all("p", {"class": "Normal"})
                articles = [tag.text for tag in article_tags]

                result["title"] = title
                result["sport_type"] = translate_sport(sport_type)
                # get author
                result["author"] = articles.pop()
                result["article"] = "\n".join(articles)

                # get image and image caption
                image_tags = soup.find_all("img", {"loading": "lazy"})
                for i in range(len(image_tags)):
                    result[f"image_{i}_url"] = image_tags[i]["data-src"]
                    result[f"image_{i}_alt"] = image_tags[i]["alt"]
                return result
    except:
        print(url)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file-path", type=str, required=True)
    parser.add_argument("--num-process", type=int, default=2)
    args = parser.parse_args()

    df = pd.read_csv(args.file_path)
    urls = df["url"].tolist()

    with mp.Pool(args.num_process) as p:
        temp_result = list(tqdm(p.imap(get_articles, urls), total=len(urls)))
        for value in temp_result:
            if value:
                collection.insert_one(value)
