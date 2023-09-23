import argparse
from crawler.loader import get_crawler

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-articles", default=100, type=int)
    parser.add_argument("--crawler-type", default="vnexpress")
    args = parser.parse_args()

    crawler = get_crawler(args.crawler_type)
    print(crawler.arguments.main_url)
