from datetime import datetime
import hashlib
import time
import scrapy
from bs4 import BeautifulSoup
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class SpiderBot(CrawlSpider):
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
        # 'HTTPCACHE_ENABLED': True,
        # 'HTTPCACHE_EXPIRATION_SECS': 3600 * 24,
        # 'HTTPCACHE_DIR': 'httpcache',
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
        'ITEM_PIPELINES': {
            'crawlerbot.pipelines.CollectItemsPipeline': 300,
        },
    }
    
    name = "spider_bot"

    rules = (
        Rule(LinkExtractor(allow=()), callback='parse_item', follow=True),
    )

    def __init__(self, start_urls=None, allowed_domains=None, link_queue_sheet=None, *args, **kwargs):
        super(SpiderBot, self).__init__(*args, **kwargs)
        self.start_urls = start_urls if start_urls else []
        self.allowed_domains = allowed_domains if allowed_domains else []
        self.link_queue_sheet = link_queue_sheet

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, meta={'start_time': time.time()})

    def parse(self, response):
        start_time = response.meta['start_time']
        url = response.url
        url_hash = hashlib.md5(url.encode()).hexdigest()
        title = response.css('title::text').get() if response.css('title::text').get() else ''

        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(['script', 'style']):
            script.extract()

        text_content = soup.get_text(separator=' ', strip=True)
        lines = (line.strip() for line in text_content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text_content = '\n'.join(chunk for chunk in chunks if chunk)

        content_hash = hashlib.md5(text_content.encode()).hexdigest()
        response_time = time.time() - start_time
        metadata = response.headers.to_unicode_dict()

        # Yield item
        yield {
            'url': url,
            'url_hash': url_hash,
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'title': title,
            'content_type': 'text/html',
            'content': text_content,
            'content_hash': content_hash,
            'response_time': response_time,
            'metadata': metadata,
            'error_code': response.status
        }

        # Extract links and add to the link queue
        if response.status == 200:
            next_pages = response.xpath('//a/@href').getall()
            for next_page in next_pages:
                next_page = response.urljoin(next_page)
                if self.link_queue_sheet:
                    self.link_queue_sheet.add_link(next_page)
                    yield scrapy.Request(next_page, callback=self.parse, meta={'start_time': time.time()})

        elif response.status == 404:
            self.log(f'Page not found: {response.url}')

        elif response.status == 403:
            self.log(f'Forbidden: {response.url}')
            self.log('Please check the robots.txt file for the website or try changing the user-agent.')

        else:
            self.log(f'Failed to download page: {response.url}')

   