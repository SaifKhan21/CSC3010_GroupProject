import hashlib
import gspread
import utility

class LinkFinishedSheet:
    '''
    This class is used to interact with the 'link_finished' sheet in the Google Sheets database.

    Headers of the 'link_finished' sheet:
    - url_hash: MD5 hash of the URL
    - url: URL of the webpage
    - datetime: Datetime of the crawl (%Y-%m-%d %H:%M:%S)
    - crawler_id: Crawler ID
    - status: Status of the crawl
    '''
    def __init__(self, client, database_id):
        self.sheet = client.open_by_key(database_id).worksheet('link_finished')
        self.finished_links = self.get_all_links_dict()

    def get_all_links(self):
        ''' Returns all the links in the 'link_finished' sheet'''
        return self.sheet.get_all_records()

    def get_all_links_dict(self):
        ''' Returns a dictionary of url: link pairs '''
        records = self.get_all_links()
        return {record['url']: record for record in records}

    def get_link(self, url):
        ''' Returns the link with the given URL 
        
            Args:
                url: str, URL of the webpage
                
            Returns:
                dict: Link with the given URL
        '''
        return url in self.finished_links

    def add_link(self, url, datetime, crawler_id, status):
        ''' Adds a new link to the 'link_finished' sheet if it does not already exist
            
                Args:
                    url: str, URL of the webpage
                    datetime: str, Datetime of the crawl (%Y-%m-%d %H:%M:%S)
                    crawler_id: str, Crawler ID
                    status: str, Status of the crawl
        
        '''
        url_hash = hashlib.md5(url.encode()).hexdigest()
        if not self.get_link(url):
            self.sheet.append_row([url_hash, url, datetime, crawler_id, status])
            self.finished_links[url] = {
                'url_hash': url_hash,
                'url': url,
                'datetime': datetime,
                'crawler_id': crawler_id,
                'status': status
            }
            print(f'Added new link to the finished links sheet: {url}')
        else:
            print(f'Link already exists in the finished links sheet: {url}')
