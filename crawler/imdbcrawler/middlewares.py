import hashlib
import json
from scrapy import signals
from scrapy.exceptions import IgnoreRequest
from scrapy.http import HtmlResponse
from scrapy.linkextractors import LinkExtractor
from queue import PriorityQueue

class ImdbcrawlerSpiderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        return None

    def process_spider_output(self, response, result, spider):
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        pass

    def process_start_requests(self, start_requests, spider):
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class ImdbcrawlerDownloaderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        s.priority_middleware = PriorityMiddleware()
        s.spider_trap_middleware = SpiderTrapMiddleware()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        self.priority_middleware.process_request(request, spider)
        return None

    def process_response(self, request, response, spider):
        response = self.spider_trap_middleware.process_response(request, response, spider)
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class PriorityMiddleware:
    def __init__(self):
        with open("keywords.json", encoding='utf-8') as f:
            self.keywords = json.load(f)

    def process_request(self, request, spider):
        priority = self.calculate_priority(request)
        request.priority = priority
        return None

    def calculate_priority(self, request):
        priority = 0
        content = request.url.lower()

        if len(content) > 10:
            priority = max(priority, 1)

        for priority_level, keywords in self.keywords.items():
            for keyword in keywords:
                if keyword.lower() in content:
                    priority = max(priority, self.get_priority_value(priority_level))
                    print(f"Keyword '{keyword}' found with priority level '{priority_level}' for URL: {request.url}")
                    break

        return priority

    def get_priority_value(self, priority_level):
        if priority_level == "high":
            return 1
        elif priority_level == "middle":
            return 0
        else:
            return -1

class SpiderTrapMiddleware:
    def __init__(self):
        self.visited_hashes = set()
        self.redirect_count = {}
        self.redirect_threshold = 5
        self.content_threshold = 3
        self.url_visit_count = {}
        self.max_visits_per_url = 10
        self.redirect_history = {}
        self.redirect_chain_limit = 5

    def process_response(self, request, response, spider):
        url = response.url

        if response.status in [301, 302]:
            if url not in self.redirect_count:
                self.redirect_count[url] = 0
            self.redirect_count[url] += 1
            if self.redirect_count[url] > self.redirect_threshold:
                raise IgnoreRequest(f"Too many redirects: {url}")
            self.track_redirect_chain(url, response.headers.get('Location'))

        if isinstance(response, HtmlResponse):
            content_hash = hashlib.md5(response.body).hexdigest()
            if content_hash in self.visited_hashes:
                raise IgnoreRequest(f"Duplicate content detected: {response.url}")
            self.visited_hashes.add(content_hash)

        if url not in self.url_visit_count:
            self.url_visit_count[url] = 0
        self.url_visit_count[url] += 1
        if self.url_visit_count[url] > self.max_visits_per_url:
            raise IgnoreRequest(f"URL visited too frequently: {url}")

        if url in self.redirect_history and len(self.redirect_history[url]) > self.redirect_chain_limit:
            raise IgnoreRequest(f"Possible infinite redirect loop detected: {url}")
        
        if response.body.count(b'\x00') > 100:
            raise IgnoreRequest(f"Ill-formed HTML with too many null characters: {response.url}")
        
        path_depth = response.url.count('/')
        if path_depth > 20:
            raise IgnoreRequest(f"Path depth too large: {response.url}")

        return response

    def track_redirect_chain(self, url, location):
        """Track the chain of redirects for a URL."""
        if url not in self.redirect_history:
            self.redirect_history[url] = []
        self.redirect_history[url].append(location)
        if len(self.redirect_history[url]) > self.redirect_chain_limit:
            self.redirect_history[url] = self.redirect_history[url][-self.redirect_chain_limit:]
