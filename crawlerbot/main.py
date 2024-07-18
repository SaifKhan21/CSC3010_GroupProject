import hashlib
import logging
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
from crawlerbot.spiders.spider_bot import SpiderBot

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


# Function to get URLs to crawl
def get_urls_to_crawl():
    urls = []
    link_queue = link_queue_sheet.get_all_links()
    
    if len(link_queue) == 0:
        link_queue_sheet.add_link(start_urls[0])
        urls.append(start_urls[0])
    else:
        while link_queue:
            link = link_queue_sheet.get_next_link()
            if link and link["url"] not in urls:
                urls.append(link["url"])
            else:
                break
    
    return urls

# Collect URLs to crawl
start_urls = ['https://www.imdb.com/']
urls_to_crawl = get_urls_to_crawl()
print(f'URLs to be crawled: {urls_to_crawl}')

# Scrapy Spider Initialization
try:
    if urls_to_crawl:
        process = CrawlerProcess(get_project_settings())
        process.crawl(SpiderBot, start_urls=urls_to_crawl, allowed_domains=['imdb.com'], link_queue_sheet=link_queue_sheet)
        process.start()

        # Ensure we get the spider and items after the crawl
        for crawler in process.crawlers:
            spider = crawler.spider
            items = getattr(spider, 'collected_items', [])
            print(f'Collected items: {items}')

            # Transfer collected items to Google Sheets
            for item in items:
                # Update Crawler Data Sheet
                crawler_data_sheet.add_data(
                    item['url_hash'],
                    item['url'],
                    item['datetime'],
                    item['title'],
                    item['content-type'],
                    item['content'],
                    len(item['content']),
                    item['content_hash'],
                    item['response_time'],
                    str(item['metadata']),
                    item['error_code']
                )
                # Update Link Finished Sheet
                link_finished_sheet.add_link(
                    item['url'],
                    item['datetime'],
                    current_crawler_id,
                    'finished'
                )
                # Update Link Queue Sheet to remove finished link
                link_queue_sheet.remove_link(item['url_hash'])

    else:
        print('No start URLs provided. Exiting...')

finally:
    crawler_sheet.set_crawler_status(current_crawler_id, 'inactive')
    print(f'Set {current_crawler_id} to inactive')