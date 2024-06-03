import os
from pathlib import Path
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import json

class ImdbSpider(CrawlSpider):
    name = 'imdb_spider'
    allowed_domains = ['imdb.com']
    start_urls = [
    # Actor search URLs
    'https://www.imdb.com/name/nm0000138/', # Leonardo DiCaprio
    'https://www.imdb.com/name/nm0424060/', # Scarlett Johansson
    'https://www.imdb.com/name/nm0000093/', # Brad Pitt
    'https://www.imdb.com/name/nm0000658/', # Meryl Streep
    'https://www.imdb.com/name/nm0000158/', # Tom Hanks
    # Top Charts and Movie URLs
    # 'https://www.imdb.com/chart/top',
    'https://www.imdb.com/title/tt0111161/', # The Shawshank Redemption
    'https://www.imdb.com/title/tt0068646/', # The Godfather
    'https://www.imdb.com/title/tt0110912/', # Pulp Fiction
    'https://www.imdb.com/title/tt0468569/', # The Dark Knight
    'https://www.imdb.com/title/tt0109830/', # Forrest Gump
    # 'https://www.imdb.com/movies-coming-soon/',
    # 'https://www.imdb.com/list/ls070819395/',
]
    # Calls the relevant method based on the URL
    def start_requests(self):
        for url in self.start_urls:
            if '/name/' in url:
                yield scrapy.Request(url, callback=self.parse_actor)
            elif '/title/' in url:
                yield scrapy.Request(url, callback=self.parse_movies)

    def parse_actor(self, response):
        actor_name = response.xpath("//title/text()").get().strip().replace(" - IMDb", "")
        json_data = response.xpath('//script[@id="__NEXT_DATA__" and @type="application/json"]/text()').get()

        data = json.loads(json_data)
        bio_text = data['props']['pageProps']['aboveTheFold']['bio']['text']['plainText']

        yield {
            'type': 'actor',
            'url': response.url,
            'actor_name': actor_name,
            'bio': bio_text[:6000]
        }

        filename = f"{actor_name}.html"
        filepath = os.path.join("downloaded_actor_pages", filename)
        Path(filepath).write_bytes(response.body)

    def parse_movies(self, response):
        movie_name = response.xpath("//title/text()").get().strip().replace(" - IMDb", "")
        plot = response.xpath('//span[@role="presentation" and @data-testid="plot-xs_to_m" and contains(@class, "sc-7193fc79-0") and contains(@class, "ftEVcu")]/text()').get()

        yield {
            'type': 'movie',
            'url': response.url,
            'movie_name': movie_name,
            'desc': plot[:6000]
        }

        filename = f"{movie_name}.html"
        filepath = os.path.join("downloaded_movie_pages", filename)
        Path(filepath).write_bytes(response.body)
    
