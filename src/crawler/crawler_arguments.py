class CrawlerArguments:
    def __init__(self, crawler_type) -> None:
        self.args_dict = {
            "vnexpress": {
                "main_url": "https://vnexpress.net",
                "available_links": [
                    "bong-da",
                    "the-thao/tennis",
                    "the-thao/marathon",
                    "the-thao/cac-mon-khac",
                    "the-thao/hau-truong",
                    "the-thao/cac-mon-khac/dua-xe",
                    "the-thao/cac-mon-khac/golf",
                    "the-thao/cac-mon-khac/co-vua",
                    "the-thao/cac-mon-khac/dien-kinh",
                ],
            },
            "dantri": {
                "main_url": "https://dantri.com.vn",
                "available_links": [
                    "the-thao/bong-da-chau-au",
                    "the-thao/tennis",
                    "the-thao/golf",
                    "the-thao/vo-thuat",
                    "the-thao/hau-truong",
                ],
            },
            "tintheothao": {
                "main_url": "https://www.tinthethao.com.vn",
                "available_links": [
                    "bong-ro",
                    "vo-thuat",
                    "quan-vot",
                    "hau-truong-the-thao",
                    "oto--xe-may",
                ],
            },
        }
        if crawler_type in self.args_dict.keys():
            self.main_url = self.args_dict[crawler_type]["main_url"]
            self.available_links = self.args_dict[crawler_type]["available_links"]
        else:
            raise ValueError("Unsupported Crawler")
