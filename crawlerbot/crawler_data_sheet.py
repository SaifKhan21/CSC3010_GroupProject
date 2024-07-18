import gspread

class CrawlerDataSheet:
    def __init__(self, client, database_id):
        self.sheet = client.open_by_key(database_id).worksheet('crawler_data')

    # Add methods to interact with the crawler data sheet
