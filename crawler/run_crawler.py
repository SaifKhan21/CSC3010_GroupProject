import sys
import os
from scrapy.cmdline import execute

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python run_spider.py <start_url> <allowed_domain>")
        sys.exit(1)

    start_url = sys.argv[1]
    allowed_domain = sys.argv[2]

    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    execute([
        "scrapy",
        "crawl",
        "imdb_crawler",
        "-a",
        f"start_url={start_url}",
        "-a",
        f"allowed_domain={allowed_domain}"
    ])
