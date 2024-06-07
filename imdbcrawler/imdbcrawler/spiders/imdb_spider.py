import hashlib
import json
import os
import sqlite3
from pathlib import Path
import re
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from collections import deque

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
    allowed_domains = ['imdb.com']
    start_urls = [
    'https://www.imdb.com'
]
    rules = (
        # Follow all links within the IMDb domain
        Rule(LinkExtractor(allow=()), callback='parse_page', follow=True),
    )

    # Breadth-first order queue
    def __init__(self, *args, **kwargs):
        super(ImdbSpider, self).__init__(*args, **kwargs)
        self.bfo_queue = deque(self.start_urls)  # Initialize a deque with start URLs
        self.init_db()

    def init_db(self):
        self.conn = sqlite3.connect('imdb_crawler.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY,
                url TEXT UNIQUE,
                crawl_date TEXT,
                content_type TEXT,
                html TEXT,
                html_hash TEXT
            )
        ''')
        self.conn.commit()

    def close_db(self):
        self.conn.close()

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
        html = response.text
        html_hash = hashlib.md5(html.encode()).hexdigest()

        self.cursor.execute('''
            INSERT OR IGNORE INTO pages (url, crawl_date, content_type, html, html_hash)
            VALUES (?, ?, ?, ?, ?)
        ''', (url, crawl_date, content_type, html, html_hash))
        self.conn.commit()

        self.log(f'Saved page {url}')

    def close(self, reason):
        self.close_db()
    
