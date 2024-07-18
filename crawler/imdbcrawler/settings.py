# Scrapy settings for imdbcrawler project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "imdb_crawler"

SPIDER_MODULES = ["simple_example.spiders"]
NEWSPIDER_MODULE = "simple_example.spiders"
SCHEDULER = "scrapy_distributed.schedulers.DistributedScheduler"
SCHEDULER_QUEUE_CLASS = "scrapy_distributed.queues.amqp.RabbitQueue"
RABBITMQ_CONNECTION_PARAMETERS = "amqp://guest:guest@localhost:5672/?heartbeat=0"
DUPEFILTER_CLASS = "scrapy_distributed.dupefilters.redis_bloom.RedisBloomDupeFilter"
BLOOM_DUPEFILTER_REDIS_URL = "redis://:@localhost:6379/0"
BLOOM_DUPEFILTER_REDIS_HOST = "localhost"
BLOOM_DUPEFILTER_REDIS_PORT = 6379
REDIS_BLOOM_PARAMS = {"redis_cls": "redisbloom.client.Client"}
BLOOM_DUPEFILTER_ERROR_RATE = 0.001
BLOOM_DUPEFILTER_CAPACITY = 100_0000

SPIDER_MODULES = ["imdbcrawler.spiders"]

FEED_FORMAT = 'jsonlines'
FEED_EXPORT_INDENT = 4

# Enable duplicate filtering
# DUPEFILTER_CLASS = 'scrapy.dupefilters.RFPDupeFilter'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 2

# LOG_FILE = None

# Disable cookies (enabled by default)
# COOKIES_ENABLED = True

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#     "Accept-Language": "en",
# }

# Directory where the crawler state will be saved
# JOBDIR = 'crawls/crawl_state'

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "imdbcrawler.middlewares.ImdbcrawlerSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "imdbcrawler.middlewares.ImdbcrawlerDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#     "imdbcrawler.pipelines.ImdbcrawlerPipeline": 300,
#     "imdbcrawler.pipelines.OverWriteFilePipeline": 1,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# AUTOTHROTTLE_START_DELAY = 1
# AUTOTHROTTLE_MAX_DELAY = 10
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"