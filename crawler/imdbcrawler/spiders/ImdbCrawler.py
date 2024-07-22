import datetime
import hashlib
from collections import deque
from sys import stderr
from traceback import print_exc

from bs4 import BeautifulSoup
from scrapy.http import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from .imdb_database import IMDBDatabase


class ImdbCrawler(CrawlSpider):
    name = 'imdb_crawler'
    start_urls = []
    allowed_domains = []

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
        'DOWNLOAD_DELAY': 2,
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
        'DEPTH_LIMIT': 50,
        'DOWNLOADER_MIDDLEWARES': {
            'imdbcrawler.middlewares.PriorityMiddleware': 100,
            'imdbcrawler.middlewares.SpiderTrapMiddleware': 200,
            'imdbcrawler.middlewares.ImdbcrawlerDownloaderMiddleware': 543,
        },
    }

    def __init__(self, *args, start_url=[], allowed_domain=[], **kwargs):
        super().__init__(*args, **kwargs)
        self.db = IMDBDatabase()
        self.start_urls = [start_url]
        self.allowed_domains = [allowed_domain]

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, callback=self.parse_page)

    def parse_page(self, response):
        try:
            if response.status == 200:
                self.save_page(response)
                links = LinkExtractor(allow=self.allowed_domains).extract_links(response)
                for link in links:
                    next_url = link.url

                    yield Request(next_url, callback=self.parse_page)
            else:
                self.log(f'Failed to download page: {response.url} with status code: {response.status}')
        except Exception as e:
            self.log(f'Error parsing page {response.url}: {e}')
            print_exc(file=stderr)

    def save_page(self, response):
        datetime_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        url = response.url
        url_hash = hashlib.md5(url.encode()).hexdigest()

        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else 'No Title'

        for script in soup(['script', 'style']):
            script.extract()

        text_content = ' '.join(filter(None, (chunk.strip() for line in soup.get_text(separator=' ').splitlines() for chunk in line.split("  "))))
        text_content_hash = hashlib.md5(text_content.encode()).hexdigest()

        metadata = str(response.headers)

        content_type = response.headers.get('Content-Type', b'').decode('utf-8') or 'Unknown'
        content_length = response.headers.get('Content-Length', b'').decode('utf-8') if 'Content-Length' in response.headers else str(len(response.body))

        with self.db as db:
            db.save_page(
                url_hash,
                url,
                datetime_str,
                content_type,
                content_length,
                title,
                text_content,
                text_content_hash,
                metadata
            )
            db.update_local_data_and_matrices()

        self.log(f'Saved page {url}')

    def __del__(self):
        if hasattr(self, 'connection'):
            self.connection.close()
