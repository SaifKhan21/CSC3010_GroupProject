# middlewares.py
import hashlib
from scrapy import signals
from scrapy.exceptions import IgnoreRequest
from scrapy.http import HtmlResponse
from scrapy.linkextractors import LinkExtractor

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
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        return None

    def process_response(self, request, response, spider):
        response = LinkAnalysisMiddleware().process_response(request, response, spider)
        response = SpiderTrapMiddleware().process_response(request, response, spider)
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class LinkAnalysisMiddleware:
    def process_response(self, request, response, spider):
        if isinstance(response, HtmlResponse):
            link_extractor = LinkExtractor()
            links = link_extractor.extract_links(response)
            # Higher priority to pages with more links
            if len(links) > 10:  # Example threshold, adjust as needed
                request.priority = 1
            else:
                request.priority = 0
        return response


class SpiderTrapMiddleware:
    def __init__(self):
        self.visited_hashes = set()
        self.redirect_count = {}
        self.redirect_threshold = 5
        self.content_threshold = 3

    def process_response(self, request, response, spider):
        # Detect too many redirects
        if response.status in [301, 302]:
            url = response.url
            if url not in self.redirect_count:
                self.redirect_count[url] = 0
            self.redirect_count[url] += 1
            if self.redirect_count[url] > self.redirect_threshold:
                raise IgnoreRequest(f"Too many redirects: {url}")

        # Detect repeated content
        if isinstance(response, HtmlResponse):
            content_hash = hashlib.md5(response.body).hexdigest()
            if content_hash in self.visited_hashes:
                raise IgnoreRequest(f"Duplicate content detected: {response.url}")
            self.visited_hashes.add(content_hash)

        return response
