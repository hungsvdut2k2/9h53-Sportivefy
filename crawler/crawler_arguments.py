class CrawlerArguments:
    def __init__(self, connection_string: str, url: str, available_links: list) -> None:
        self.db_connection = connection_string
        self.main_url = url
        self.available_links = available_links
