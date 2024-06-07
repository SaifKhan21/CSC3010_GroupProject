import hashlib
import json
import os
import re
import sqlite3
from collections import deque
from pathlib import Path
# from imdbcrawler.imdb_database import IMDBDatabase # run this when running flask
from imdb_database import IMDBDatabase # run this when running scrap

import scrapy
from bs4 import BeautifulSoup
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

class ImdbSpider(CrawlSpider):
    name = 'imdb_spider'

    # Header to bypass 403 forbidden error
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",  # Do Not Track Request Header
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

    # Restricts the spider to only crawl URLs under the IMDb domain
    allowed_domains = ['crawler-test.com']
    start_urls = [
    'https://www.crawler-test.com'
    ]

    rules = (
        # Follow all links within the IMDb domain
        Rule(LinkExtractor(allow=()), callback='parse_page', follow=True),
    )

    custom_settings = {
        #allow duplicate requests
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        # Disable cookies (enabled by default)
        'COOKIES_ENABLED': False,
        # Obey robots.txt rules
        'ROBOTSTXT_OBEY': True,
        # Configure maximum concurrent requests performed by Scrapy (default: 16)
        'CONCURRENT_REQUESTS': 16,
        # Configure a delay for requests for the same website (default: 0)
        'DOWNLOAD_DELAY': 2,
        # The download delay setting will honor only one of:
        'CONCURRENT_REQUESTS_PER_DOMAIN': 16,
        'CONCURRENT_REQUESTS_PER_IP': 16,
        # Override the default request headers:
        'DEFAULT_REQUEST_HEADERS': {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",  # Do Not Track Request Header
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        },
        # Directory where the crawler state will be saved
        'JOBDIR': 'crawls/crawl_state',
    }

    # Breadth-first order queue
    def __init__(self, *args, **kwargs):
        ''''
        Initialize the spider and create a deque with start URLs
        
        The deque is used to implement a breadth-first order (BFO) crawling strategy'''
        super(ImdbSpider, self).__init__(*args, **kwargs)
        self.bfo_queue = deque(self.start_urls)  # Initialize a deque with start URLs
        self.database = IMDBDatabase()

    def start_requests(self):
        while self.bfo_queue:
            url = self.bfo_queue.popleft()  # Pop the first URL from the queue
            yield scrapy.Request(url, callback=self.parse_page, priority=0)

    def parse_page(self, response):
        # Save the page content
        self.save_page(response)

        # Extract links and add them to the BFO queue
        next_pages = response.xpath('//a/@href').getall()
        for next_page in next_pages:
            next_page = response.urljoin(next_page)
            # Filters out non-HTTP links and avoids adding duplicate URLs to the queue
            if next_page.startswith('http') and next_page not in self.bfo_queue:
                self.bfo_queue.append(next_page)
                yield scrapy.Request(next_page, callback=self.parse_page, priority=0)

    def save_page(self, response):
        # Create a directory to store downloaded pages if it doesn't exist
        url = response.url
        crawl_date = response.headers.get('Date', '').decode('utf-8')
        content_type = response.headers.get('Content-Type', '').decode('utf-8')

        # Fully save the HTML content in the page to the database
        # html = response.text
        # html_hash = hashlib.md5(html.encode()).hexdigest()

        # Brute-force method to extract text content from HTML
        # text_content = response.xpath('//body//text()').getall()
        # text_content = ' '.join(text_content)
        # # Remove HTML, scripts, styles, code, CSS styles, and JSON/GraphQL-like structures
        # text_content = re.sub(r'<(script|style)[^>]*?>.*?</\1>', '', text_content, flags=re.DOTALL)
        # text_content = re.sub(r'<.*?>', '', text_content)
        # text_content = re.sub(r'\b(function|var|let|const|if|else|for|while|switch|case|default|return|this|new|try|catch|finally)\b', '', text_content)
        # text_content = re.sub(r'[{}\[\]();,]', '', text_content)
        # text_content = re.sub(r'\b[\w-]+:[\w-]+;?', '', text_content)
        # text_content = re.sub(r'"([^"]*)":\s*"([^"]*)"', '', text_content)  # Remove key-value pairs
        # text_content = re.sub(r'\[[^\]]*\]', '', text_content)         # Remove arrays
        # text_content = re.sub(r'\b(true|false|null)\b', '', text_content)    # Remove booleans and null
        # # Remove remaining numerical and boolean values
        # text_content = re.sub(r'\b\d+\.?\d*\b', '', text_content)  # Remove numbers (optional)
        # text_content = re.sub(r'\s+', ' ', text_content).strip()

        # Extract text content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(['script', 'style']):
            script.extract()
        
        text_content = soup.get_text()
        lines = (line.strip() for line in text_content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text_content = '\n'.join(chunk for chunk in chunks if chunk)

        text_hash = hashlib.md5(text_content.encode()).hexdigest()

        with self.database as db:
            db.save_page(url, crawl_date, content_type, text_content, text_hash)

        self.log(f'Saved page {url}')

