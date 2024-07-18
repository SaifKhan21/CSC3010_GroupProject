import hashlib
import gspread
import utility

class LinkQueueSheet:
    '''
    This class is used to interact with the 'link_queue' sheet in the Google Sheets database.

    Headers of the 'link_queue' sheet:
    - url_hash: MD5 hash of the URL
    - url: URL of the webpage
    - crawler_id: Crawler ID
    - progress: Progress of the crawl (None, pending)
    - datetime_added: Datetime of the addition to the queue (%Y-%m-%d %H:%M:%S)
    - attempts: Number of attempts to crawl the webpage
    - datetime_attempted: Datetime of the last crawl attempt (%Y-%m-%d %H:%M:%S)
    - priority: Priority of the webpage

    '''
    def __init__(self, client, database_id):
        self.sheet = client.open_by_key(database_id).worksheet('link_queue')
        self.link_queue = self.get_all_links_dict()

    def get_all_links(self):
        ''' Returns all the links in the 'link_queue' sheet '''
        return self.sheet.get_all_records()

    def get_all_links_dict(self):
        ''' Returns a dictionary of url_hash: link pairs '''
        records = self.get_all_links()
        return {record['url_hash']: record for record in records}

    def add_link(self, url):
        ''' Adds a new link to the 'link_queue' sheet if it does not already exist

            Args:
                url: str, URL of the webpage
        '''
        url_hash = hashlib.md5(url.encode()).hexdigest()
        if url_hash in self.link_queue:
            print(f'Link already exists in the link queue: {url}')
            return

        new_link = {
            'url_hash': url_hash,
            'url': url,
            'crawler_id': None,
            'progress': None,
            'datetime_added': utility.get_current_time(),
            'attempts': 0,
            'datetime_attempted': None,
            'priority': 0
        }
        self.sheet.append_row(list(new_link.values()))
        self.link_queue[url_hash] = new_link
        print(f'Added new link to the link queue: {url}')

    def get_next_link(self):
        ''' Returns the link with the highest priority from the 'link_queue' sheet 
            If multiple links have the same priority, the one added first is returned
        
            Returns:
                dict: Link with the highest priority that has no progress
        '''
        if not self.link_queue:
            return None
        # Filter links with empty 'progress'
        filtered_links = [link for link in self.link_queue.values() if not link['progress']]
        if not filtered_links:
            return None
        sorted_links = sorted(filtered_links, key=lambda x: (x['priority'], x['datetime_added']))
        return sorted_links[0]

    def update_link(self, url_hash, crawler_id, progress, datetime_attempted):
        ''' Updates the link in the 'link_queue' sheet with the given URL hash
        
            Args:
                url_hash: str, URL hash of the webpage
                crawler_id: str, Crawler ID
                progress: str, Progress of the crawl
                datetime_attempted: str, Datetime of the last crawl attempt (%Y-%m-%d %H:%M:%S)
        '''
        if url_hash in self.link_queue:
            link = self.link_queue[url_hash]
            row = list(self.link_queue.keys()).index(url_hash) + 2  # +2 to account for header and 0-indexing
            new_attempts = link['attempts'] + 1
            self.sheet.update_cell(row, 3, crawler_id)
            self.sheet.update_cell(row, 4, progress)
            self.sheet.update_cell(row, 6, new_attempts)
            self.sheet.update_cell(row, 7, datetime_attempted)
            link['crawler_id'] = crawler_id
            link['progress'] = progress
            link['attempts'] = new_attempts
            link['datetime_attempted'] = datetime_attempted
            print(f'Updated link in the link queue: {link["url"]}')
            return True
        else:
            print(f'Link does not exist in the link queue: {url_hash}')
            return False
            
    def remove_link(self, url_hash):
        ''' Removes the link with the given URL hash from the 'link_queue' sheet
        
            Args:
                url_hash: str, URL hash of the webpage
        '''
        if url_hash in self.link_queue:
            row = list(self.link_queue.keys()).index(url_hash) + 2  # +2 to account for header and 0-indexing
            self.sheet.delete_rows(row)
            del self.link_queue[url_hash]
            print(f'Removed link from the link queue: {url_hash}')
        else:
            print(f'Link does not exist in the link queue: {url_hash}')
