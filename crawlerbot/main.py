import hashlib
import gspread
import scrapy
import utility
from google.oauth2.service_account import Credentials
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from crawler_sheet import CrawlerSheet
from link_queue_sheet import LinkQueueSheet
from link_finished_sheet import LinkFinishedSheet
from crawler_data_sheet import CrawlerDataSheet
# from crawlerbot.spiders.spider_bot import SpiderBot

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
]
creds = Credentials.from_service_account_file('csc3010-3222a271adf7.json', scopes=scopes)
client = gspread.authorize(creds)

database_id = '1ckuJUP82WHljsT-D5lVKIBlCtoV-HAmA91kRGXgmqbg'

crawler_sheet = CrawlerSheet(client, database_id)
link_queue_sheet = LinkQueueSheet(client, database_id)
link_finished_sheet = LinkFinishedSheet(client, database_id)
crawler_data_sheet = CrawlerDataSheet(client, database_id)

start_urls = ['https://www.imdb.com/']

# Crawler sheet logic
current_crawler_id = utility.get_mac_address()
current_crawler_id = hashlib.md5(current_crawler_id.encode()).hexdigest()

crawler_sheet.set_crawler_active(current_crawler_id)

# Link Queue Logic
link_queue = link_queue_sheet.get_all_links()

if len(link_queue) == 0:
    link_queue_sheet.add_link(start_urls[0])
else:
    link = link_queue_sheet.get_next_link()
    if link:
        print(f'Link to be crawled: {link["url"]}')

# Link Finished Logic
finished_links = link_finished_sheet.get_all_links_dict()

# Crawler Data Logic
crawler_data_sheet.update_local_data_and_matrices()
all_data = crawler_data_sheet.get_all_data_dict()

# Scrapy Spider Initialization
# settings = get_project_settings()
# process = CrawlerProcess(settings)

try:
    # process.crawl(SpiderBot, start_urls=start_urls)
    # process.start()
    pass
finally:
    crawler_sheet.set_crawler_status(current_crawler_id, 'inactive')
    print(f'Set {current_crawler_id} to inactive')
