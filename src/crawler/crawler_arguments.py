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
                ],
            }
        }
        if crawler_type in self.args_dict.keys():
            self.main_url = self.args_dict[crawler_type]["main_url"]
            self.available_links = self.args_dict[crawler_type]["available_links"]
        else:
            raise ValueError("Unsupported Crawler")
