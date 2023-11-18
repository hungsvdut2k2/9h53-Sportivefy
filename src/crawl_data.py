import argparse
import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from src.crawler.crawler_factory import get_crawler


def get_collection(connection_string: str, database_name: str):
    client = MongoClient(connection_string, server_api=ServerApi("1"))
    database = client["articles"]
    collection = database[database_name]
    return collection


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--crawler-type", type=str, required=True)
    parser.add_argument("--num-pages", type=int, default=1)
    args = parser.parse_args()

    load_dotenv()
    connection_string = os.getenv("CONNECTION_STRING")
    collection = get_collection(connection_string, args.crawler_type)

    crawler = get_crawler(crawler_type=args.crawler_type)

    urls_list = crawler.get_urls(num_pages=args.num_pages)
    articles = crawler.get_articles(url_list=urls_list)
    collection.insert_many(articles)
