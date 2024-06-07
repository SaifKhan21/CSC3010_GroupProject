from flask import Flask
from scrapy.crawler import CrawlerProcess
from imdbcrawler.imdbcrawler.spiders.imdb_spider import ImdbSpider

app = Flask(__name__)

process = None

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/start_crawl')
def start_crawl():
    global process
    if process:
        return 'Crawling is already in progress...'
    process = CrawlerProcess()
    process.crawl(ImdbSpider)
    print('Crawling IMDb...')
    process.start(stop_after_crawl=False)
    return 'Crawling IMDb...'

@app.route('/end_crawl')
def end_crawl():
    global process
    if process is not None:
        print('Ending the crawl...')
        process.stop()
        process = None
        return 'Ending the crawl...'
    else:
        return 'No crawl is currently running.'


if __name__ == '__main__':
    app.run()