import threading

from flask import Flask, render_template_string
from scrapy.crawler import CrawlerProcess

from crawler.imdb_database import IMDBDatabase
from crawler.imdbcrawler.spiders.imdb_spider import ImdbSpider

app = Flask(__name__)

# CrawlerProcess in a thread
crawler_thread = None

@app.route('/')
def hello():
    return "Welcome to the IMDb Crawler API! Use '/start_crawl' to start and '/end_crawl' to stop."

@app.route('/start_crawl')
def start_crawl():
    global crawler_thread

    if crawler_thread and crawler_thread.is_alive():
        return "Crawling is already in progress...", 202  # Return "Accepted"

    def run_crawl():
        process = CrawlerProcess()
        process.crawl(ImdbSpider)
        process.start()

    crawler_thread = threading.Thread(target=run_crawl)
    crawler_thread.start()

    return "Crawling started successfully.", 201  # Return "Created"

@app.route('/end_crawl')
def end_crawl():
    global crawler_thread

    if crawler_thread:
        crawler_thread.join(timeout=5) # Graceful shutdown with a 5-second timeout

        if crawler_thread.is_alive():  # If still running, terminate forcefully
            crawler_process = crawler_thread._target.__self__  # Access the CrawlerProcess instance
            crawler_process.stop()

        crawler_thread = None
        return "Crawl stopped forcefully.", 200
    else:
        return "No crawl is currently running.", 409
    
@app.route('/crawl_data')
def crawl_data():
    with IMDBDatabase() as db:
        data = db.get_all_data()

    if not data:
        return "No data found in the database.", 404

    table_html = """
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
    </style>
    <table>
        <tr>
            <th>URL</th>
            <th>Crawl Date</th>
            <th>Content Type</th>
            <th>Content</th>
        </tr>
        {% for row in data %}
        <tr>
            <td>{{ row[0] }}</td>
            <td>{{ row[1] }}</td>
            <td>{{ row[2] }}</td>
            <td>{{ row[3] }}</td> 
        </tr>
        {% endfor %}
    </table>
    """

    return render_template_string(table_html, data=data)

@app.route('/check_crawl')
def check_crawl():
    if crawler_thread and crawler_thread.is_alive():
        return "Crawling in progress.", 200
    else:
        return "Crawler is not running.", 404

if __name__ == '__main__':
    app.run()
