import hashlib
import gspread

class CrawlerSheet:
    def __init__(self, client, database_id):
        self.sheet = client.open_by_key(database_id).worksheet('crawlers')

    def get_all_crawler_ids(self):
        return self.sheet.col_values(1)

    def add_crawler(self, crawler_id):
        self.sheet.append_row([crawler_id, 'inactive'])

    def set_crawler_status(self, crawler_id, status):
        crawler_ids = self.get_all_crawler_ids()
        if crawler_id in crawler_ids:
            row = crawler_ids.index(crawler_id) + 1
            self.sheet.update_cell(row, 2, status)
        else:
            self.add_crawler(crawler_id)
            row = len(crawler_ids) + 1
            self.sheet.update_cell(row, 2, status)

    def get_crawler_status(self, crawler_id):
        crawler_ids = self.get_all_crawler_ids()
        if crawler_id in crawler_ids:
            row = crawler_ids.index(crawler_id) + 1
            return self.sheet.cell(row, 2).value
        return None

    def set_crawler_active(self, crawler_id):
        crawler_ids = self.get_all_crawler_ids()
        if crawler_id not in crawler_ids:
            self.add_crawler(crawler_id)
            print(f'Added new crawler_id: {crawler_id}')
        else:
            print(f'Found existing crawler_id: {crawler_id}')

        current_status = self.get_crawler_status(crawler_id)
        if current_status != 'active':
            self.set_crawler_status(crawler_id, 'active')
            print(f'Set {crawler_id} to active')

    def set_crawler_inactive(self, crawler_id):
        self.set_crawler_status(crawler_id, 'inactive')