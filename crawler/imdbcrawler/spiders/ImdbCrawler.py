import datetime
import hashlib
from collections import deque
from html.parser import HTMLParser
from re import sub
from sys import stderr
from traceback import print_exc
from urllib.parse import urlparse

import scrapy
from bs4 import BeautifulSoup
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from .imdb_database import IMDBDatabase


class _DeHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.__text = []

    def handle_data(self, data):
        text = data.strip()
        if len(text) > 0:
            text = sub('[ \t\r\n]+', ' ', text)
            self.__text.append(text + ' ')

    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            self.__text.append('\n\n')
        elif tag == 'br':
            self.__text.append('\n')

    def handle_startendtag(self, tag, attrs):
        if tag == 'br':
            self.__text.append('\n\n')

    def text(self):
        return ''.join(self.__text).strip()

def dehtml(text):
    try:
        parser = _DeHTMLParser()
        parser.feed(text)
        parser.close()
        return parser.text()
    except Exception:
        print_exc(file=stderr)
        return text

class ImdbCrawler(CrawlSpider):
    name = 'imdb_crawler'
    start_urls = ['https://www.imdb.com/']
    allowed_domains = ['imdb.com']

    rules = (
        Rule(LinkExtractor(allow=()), callback='parse_page', follow=True),
    )

    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'COOKIES_ENABLED': False,
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': 32,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 16,
        'CONCURRENT_REQUESTS_PER_IP': 16,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 2,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'HTTPCACHE_ENABLED': True,
        'HTTPCACHE_EXPIRATION_SECS': 3600 * 24,
        'HTTPCACHE_DIR': 'httpcache',
        'DOWNLOAD_DELAY': 0.25,
        'DOWNLOAD_TIMEOUT': 15,
        'RETRY_TIMES': 3,
        'RETRY_HTTP_CODES': [500, 503, 504, 400, 403, 404, 408],
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'DEFAULT_REQUEST_HEADERS': {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1", 
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        },
    }

    def __init__(self, *args, **kwargs):
        super(ImdbCrawler, self).__init__(*args, **kwargs)
        self.bfo_queue = deque(self.start_urls)
        self.db = IMDBDatabase()

    def start_requests(self):
        while self.bfo_queue:
            url = self.bfo_queue.popleft()
            yield scrapy.Request(url, callback=self.parse_page, priority=0)

    def parse_page(self, response):
        if response.status == 200:
            self.save_page(response)

            # Extract links and add them to the BFO queue
            next_pages = response.xpath('//a/@href').getall()
            for next_page in next_pages:
                next_page = response.urljoin(next_page)
                if next_page not in self.bfo_queue:
                    self.bfo_queue.append(next_page)
                    yield scrapy.Request(next_page, callback=self.parse_page, priority=0)

        elif response.status == 404:
            self.log(f'Page not found: {response.url}')
        elif response.status == 403:
            self.log(f'Forbidden: {response.url}')
            self.log('Please check the robots.txt file or try changing the user-agent.')
        else:
            self.log(f'Failed to download page: {response.url}')

    def save_page(self, response):
        datetime_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        url = response.url
        url_hash = hashlib.md5(url.encode()).hexdigest()

        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else 'No Title'

        raw_html = response.text
        html = dehtml(raw_html)
        html_hash = hashlib.md5(html.encode()).hexdigest()

        metadata = str(response.headers)

        content_type = response.headers.get('Content-Type').decode('utf-8') if response.headers.get('Content-Type') else 'Unknown'
        content_length = response.headers.get('Content-Length').decode('utf-8') if response.headers.get('Content-Length') else 'Unknown'

        with self.db as db:
            db.save_page(url_hash,
                        url,
                        datetime_str,
                        content_type,
                        content_length,
                        title,
                        html,
                        html_hash,
                        metadata)
            db.update_local_data_and_matrices()

        self.log(f'Saved page {url}')

    def __del__(self):
        if hasattr(self, 'connection'):
            self.connection.close()
