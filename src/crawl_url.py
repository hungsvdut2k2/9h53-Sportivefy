import argparse
from src.crawler.crawler_factory import get_crawler

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--crawler-type", type=str, required=True)
    parser.add_argument("--num-pages", type=int, default=1)
    parser.add_argument("--output-file", type=str)
    args = parser.parse_args()

    crawler = get_crawler(crawler_type=args.crawler_type)
    urls = crawler.get_urls(num_pages=args.num_pages)

    with open(args.output_file, "w") as f:
        for url in urls:
            f.writelines(f"{url}\n")
