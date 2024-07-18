import hashlib
import gspread
import utility

class LinkQueueSheet:
    def __init__(self, client, database_id):
        self.sheet = client.open_by_key(database_id).worksheet('link_queue')

    def get_all_links(self):
        return self.sheet.get_all_records()

    def add_link(self, url):
        url_hash = hashlib.md5(url.encode()).hexdigest()
        self.sheet.append_row([
            url_hash,
            url,
            None,
            'not started',
            utility.get_current_time(),
            0,
            None,
            0
        ])

    def get_next_link(self):
        link_queue = self.get_all_links()
        if not link_queue:
            return None
        link_queue = sorted(link_queue, key=lambda x: (x['priority'], x['datetime_added']))
        return link_queue[0]
