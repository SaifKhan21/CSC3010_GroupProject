import hashlib
from collections import deque

import nltk
import scrapy
from bs4 import BeautifulSoup
from crawler.imdb_database import IMDBDatabase # run this when running flask
#from imdb_database import IMDBDatabase  # run this when running scrapy
from nltk.corpus import stopwords
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class ImdbSpider(CrawlSpider):
    '''
    A Scrapy spider that crawls the IMDb website in a breadth-first order (BFO) and 
    saves the page content to a SQLite database.
    The spider starts from the IMDb homepage and follows all links within the IMDb domain.
    It saves the page content to a SQLite database, including the URL, crawl date,
    content type, HTML content, and a hash of the HTML content.
    The spider uses a breadth-first order (BFO) crawling strategy to visit 
    pages in a level-by-level manner.
    '''
    name = 'imdb_spider'

    # Restricts the spider to only crawl URLs under the allowed domain and subdomains
    allowed_domains = ['imdb.com']
    start_urls = [
    'https://www.imdb.com'
    ]
    # allowed_domains = ['crawler-test.com']
    # start_urls = [
    # 'https://www.crawler-test.com'
    # ]

    # Rules for following links within the allowed domains
    rules = (
        Rule(LinkExtractor(allow=()), callback='parse', follow=True),
    )

    # Custom settings for the spider
    custom_settings = {
        # allow duplicate filtering
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'COOKIES_ENABLED': False,
        'ROBOTSTXT_OBEY': True,

        # Configure maximum concurrent requests performed by Scrapy (default: 16)
        'CONCURRENT_REQUESTS': 32,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 16,
        'CONCURRENT_REQUESTS_PER_IP': 16,

        # Autothrottle settings
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 2,
        'AUTOTHROTTLE_MAX_DELAY': 60,

        # Http cache settings
        'HTTPCACHE_ENABLED': True,
        'HTTPCACHE_EXPIRATION_SECS': 3600 * 24,
        'HTTPCACHE_DIR': 'httpcache',
        
        # Download Settings
        'DOWNLOAD_DELAY': 0.25, # delay before downloading the next page
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
        
        # Directory where the crawler state will be saved
        'JOBDIR': 'crawls/crawl_state',
    }
    stop_words = None

    # Breadth-first order queue
    def __init__(self, *args, **kwargs):
        ''''
        Initialize the spider and create a deque with start URLs
        
        The deque is used to implement a breadth-first order (BFO) crawling strategy
        '''
        super(ImdbSpider, self).__init__(*args, **kwargs)
        self.bfo_queue = deque(self.start_urls)
        self.database = IMDBDatabase()
        nltk.download('stopwords')
        self.stop_words = set(stopwords.words('english'))

    def start_requests(self):
        '''
        Start the BFO crawl by yielding requests for the start URLs
        
        Returns:
            scrapy.Request: The first request to start the BFO crawl    
        '''
        while self.bfo_queue:
            url = self.bfo_queue.popleft()  # Pop the first URL from the queue
            yield scrapy.Request(url, callback=self.parse_page, priority=0)

    def parse_page(self, response, **kwargs):
        '''
        Parse the page content and extract links to add to the BFO queue. 
        Save the page content to the database.
        '''
        if response.status == 200:
            # Save the page content
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
            self.log('Please check the robots.txt file for the website or try changing the user-agent.')
            
        else:
            self.log(f'Failed to download page: {response.url}')

    def save_page(self, response):
        '''
        Save the page content to the database
        
        Args:
            response (scrapy.http.Response): The response object containing the page content
        '''
        # Create a directory to store downloaded pages if it doesn't exist
        url = response.url
        crawl_date = response.headers.get('Date', '').decode('utf-8')
        content_type = response.headers.get('Content-Type', '').decode('utf-8')

        # Extract text content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(['script', 'style']):
            script.extract()

        text_content = soup.get_text(separator=' ', strip=True)
        lines = (line.strip() for line in text_content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text_content = '\n'.join(chunk for chunk in chunks if chunk)

        word_tokens = text_content.split()
        filtered_text_content = ' '.join(
            [word for word in word_tokens if word.lower() not in self.stop_words]
            )

        text_hash = hashlib.md5(filtered_text_content.encode()).hexdigest()

        with self.database as db:
            db.save_page(url, crawl_date, content_type, filtered_text_content, text_hash)

        self.log(f'Saved page {url}')
