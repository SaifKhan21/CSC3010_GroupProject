import hashlib
import gspread

class CrawlerSheet:
    '''
    This class is used to interact with the 'crawlers' sheet in the Google Sheets database.

    Headers of the 'crawlers' sheet:
    - crawler_id: Crawler ID
    - status: Status of the crawler
    '''
    def __init__(self, client, database_id):
        self.sheet = client.open_by_key(database_id).worksheet('crawlers')
        self.crawler_data = self.get_all_crawlers_dict()

    def get_all_crawlers_dict(self):
        ''' Returns a dictionary of crawler_id: status pairs '''
        records = self.sheet.get_all_records()
        return {record['crawler_id']: record['status'] for record in records}

    def add_crawler(self, crawler_id):
        ''' Adds a new crawler to the 'crawlers' sheet with status 'inactive' 
            if it does not already exist 
            
            Args:
                crawler_id: str, Crawler ID
        '''
        self.sheet.append_row([crawler_id, 'inactive'])
        self.crawler_data[crawler_id] = 'inactive'

    def set_crawler_status(self, crawler_id, status):
        ''' Sets the status of a crawler in the 'crawlers' sheet
                
            Args:
                crawler_id: str, Crawler ID
                status: str, Status of the crawler
        '''
        if crawler_id in self.crawler_data:
            row = list(self.crawler_data.keys()).index(crawler_id) + 2  # +2 to account for header and 0-indexing
            self.sheet.update_cell(row, 2, status)
        else:
            self.add_crawler(crawler_id)
            row = len(self.crawler_data) + 1
            self.sheet.update_cell(row + 1, 2, status)  # row + 1 to account for header
        self.crawler_data[crawler_id] = status

    def get_crawler_status(self, crawler_id):
        ''' Returns the status of a crawler from the 'crawlers' sheet
        
            Args:
                crawler_id: str, Crawler ID
        '''
        return self.crawler_data.get(crawler_id, None)

    def set_crawler_active(self, crawler_id):
        ''' Sets the status of a crawler to 'active' in the 'crawlers' sheet
        
            Args:
                crawler_id: str, Crawler ID
        '''
        if crawler_id not in self.crawler_data:
            self.add_crawler(crawler_id)
            print(f'Added new crawler_id: {crawler_id}')
        else:
            print(f'Found existing crawler_id: {crawler_id}')

        current_status = self.get_crawler_status(crawler_id)
        if current_status != 'active':
            self.set_crawler_status(crawler_id, 'active')
            print(f'Set {crawler_id} to active')

    def set_crawler_inactive(self, crawler_id):
        ''' Sets the status of a crawler to 'inactive' in the 'crawlers' sheet
        
            Args:
                crawler_id: str, Crawler ID
        '''
        self.set_crawler_status(crawler_id, 'inactive')
