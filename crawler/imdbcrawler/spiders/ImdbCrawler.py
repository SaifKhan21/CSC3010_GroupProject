import datetime
import hashlib

from bs4 import BeautifulSoup
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from .imdb_database import IMDBDatabase


class ImdbCrawler(CrawlSpider):
    name = 'imdb_crawler'

    available_start_urls = ['https://www.imdb.com/', # IMDb Home
                            'https://www.imdb.com/chart/top/', # Top Rated Movies
                            'https://www.imdb.com/chart/tvmeter/?ref_=nv_tvv_mptv', # TV Shows
                            'https://www.imdb.com/emmys/?ref_=nv_ev_csegemy', # Emmy Awards
                            'https://www.imdb.com/chart/starmeter/?ref_=nv_cel_m' # Celebrity
                            ]
    
    allowed_domains = ['www.imdb.com']

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
        'DEPTH_LIMIT': 25,
    }

    def __init__(self, *args, start_url_index=0, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = IMDBDatabase()

        # Set start_urls based on the given index
        if 0 <= start_url_index < len(self.available_start_urls):
            self.start_urls = [self.available_start_urls[start_url_index]]
        else:
            raise ValueError(f'start_url_index {start_url_index} is out of range. Must be between 0 and {len(self.available_start_urls) - 1}.')


    def parse_page(self, response):
        try:
            if response.status == 200:
                self.save_page(response)
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
