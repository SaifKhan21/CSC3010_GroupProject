import hashlib
import gspread
import scrapy
import utility
from google.oauth2.service_account import Credentials
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from crawlerbot.spiders.spider_bot import SpiderBot

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
]
creds = Credentials.from_service_account_file('csc3010-5db0d06aeca2.json', scopes=scopes)
client = gspread.authorize(creds)

database_id = '1ckuJUP82WHljsT-D5lVKIBlCtoV-HAmA91kRGXgmqbg'
database = client.open_by_key(database_id)

sheet_names = database.sheet1.spreadsheet.worksheets()
sheet_names = [sheet.title for sheet in sheet_names]

# All the sheets in the Google Sheets database. Row 1 is the header row.
crawler_sheet = database.sheet1.spreadsheet.worksheet('crawlers')
link_queue_sheet = database.sheet1.spreadsheet.worksheet('link_queue')
link_finished_sheet = database.sheet1.spreadsheet.worksheet('link_finished')
crawler_data_sheet = database.sheet1.spreadsheet.worksheet('crawler_data')

start_urls = ['https://www.imdb.com/']

# Crawler sheet logic
# Headers for the Crawler sheet: crawler_id	status
current_crawler_id = utility.get_mac_address()
current_crawler_id = hashlib.md5(current_crawler_id.encode()).hexdigest()
crawler_row = None

# Check if the crawler_id already exists in the 'crawlers' sheet
crawler_ids = crawler_sheet.col_values(1)
if current_crawler_id not in crawler_ids:
    # If not, add the new crawler_id with 'inactive' status
    crawler_sheet.append_row([current_crawler_id, 'inactive'])
    crawler_row = len(crawler_ids) + 1
    print(f'Added new crawler_id: {current_crawler_id}')
else:
    crawler_row = crawler_ids.index(current_crawler_id) + 1
    print(f'Found existing crawler_id: {current_crawler_id}')

# set the current crawler_id to active if it is not already active
current_status = crawler_sheet.cell(crawler_row, 2).value
if current_status != 'active':
    crawler_sheet.update_cell(crawler_row, 2, 'active')
    print(f'Set {current_crawler_id} to active')

# Link Queue Logic
# Headers for the Link Queue sheet: url_hash	url	crawler_id	progress	datetime_added	attempts	datetime_attempted	priority
if link_queue_sheet.row_count < 2:
    # hash the url using md5
    start_url_hash = hashlib.md5(start_urls[0].encode()).hexdigest()
    link_queue_sheet.append_row([start_url_hash,
                                start_urls[0],
                                current_crawler_id,
                                'not started', 
                                utility.get_current_time(),
                                0,
                                None,
                                0]
                                )
    print(f'Added new link to the queue: {start_urls[0]}')
else:
    # Get the first link with the lowest priority and earliest datetime_added
    # Ignoring the first header row
    link_queue = link_queue_sheet.get_all_records()
    link_queue = link_queue[1:]
    link_queue = sorted(link_queue, key=lambda x: (x['priority'], x['datetime_added']))
    link = link_queue[0]
    print(f'Link to be crawled: {link["url"]}')


# # Scrapy Spider Initialization
# settings = get_project_settings()
# process = CrawlerProcess(settings)


try:
    # process = CrawlerProcess(get_project_settings())
    # spider = SpiderBot()
    # process.crawl(SpiderBot, start_urls=start_urls)
    # process.start()

    #items = spider.collect_items()
    pass
finally:
    # Set the current crawler_id to inactive when the process finishes
    crawler_sheet.update_cell(crawler_row, 2, 'inactive')
    print(f'Set {current_crawler_id} to inactive')
