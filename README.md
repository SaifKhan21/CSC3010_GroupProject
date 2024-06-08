# CSC3010 Group Project
## IMDB Crawler

### Setup
1. To create a virtual environment:
```
python -m venv venv

(Windows)
venv\bin\activate

(Mac)
. ./venv/bin/activate
```
2. Load the requirements
```
pip install -r requirements.txt
```

3. Run the Flask Application

If running the flask application, remember to uncomment `line 7` and comment `line 8` in `crawler\imdbcrawler\spiders\imdb_spiders.py`. The imports should look like this.
```
from crawler.imdb_database import IMDBDatabase # run this when running flask
#from imdb_database import IMDBDatabase  # run this when running scrapy
```

To run the flask application, type:
```
python main.py
```
Access the URL through your browser. The following links are:
```
Start the crawling process - 127.0.0.1:5000/start_crawl
End the crawling process - 127.0.0.1:5000/end_crawl
Check the crawling process - 127.0.0.1:5000/check_crawl
Check the crawled data - 127.0.0.1:5000/crawl_data
```

### Testing crawler
If you want to test the scraper, comment line 7 and uncomment line 8 in `crawler\imdbcrawler\spiders\imdb_spiders.py`.
```
#from crawler.imdb_database import IMDBDatabase # run this when running flask
from imdb_database import IMDBDatabase  # run this when running scrapy
```

To run the scraper, type:
```
cd crawler
scrapy crawl imdb_spider
```

### Database

Database will be using `sqlite`. The file will be in the tree somewhere denoted by the `.db` extension. You may use [SQLite Viewer](https://inloop.github.io/sqlite-viewer/) to help you view the database. 

## Lucene Engine

### Setup
1. Download and install [IntelliJ Community Edition](https://www.jetbrains.com/idea/download/download-thanks.html?platform=windows&code=IIC) (Windows download)

2. Download and install Lucene 9.11.0:

Download the Lucene package [here.](https://dlcdn.apache.org/lucene/java/9.11.0/lucene-9.11.0.tgz)

Extract the lucene-9.11.0 folder directly into your C drive folder (C:\lucene-9.11.0)

### Running the Engine
Open up the project using IntelliJ and run the Java file from there.

Ensure that you're opening the project folder (lucene-test) and not the base github folder, otherwise dependencies won't load properly.