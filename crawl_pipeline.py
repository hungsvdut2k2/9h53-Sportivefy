import argparse
from crawler.crawler_arguments import CrawlerArguments
from crawler.thethao24h_crawler import TheThao24hCrawler
from utils import convert_crawler_to_url, map_crawler_available_list

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-articles", default=100, type=int)
    parser.add_argument("--crawler-type", default="thethao247")
    args = parser.parse_args()

    main_url = convert_crawler_to_url(args.crawler_type)

    crawler_args = CrawlerArguments(
        connection_string="cho beo",
        url=main_url,
        available_links=map_crawler_available_list(main_url),
    )
    crawler = TheThao24hCrawler(crawler_args)
    crawler.load_main_page()
