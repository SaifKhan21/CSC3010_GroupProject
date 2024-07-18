# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import logging
from itemadapter import ItemAdapter


class CrawlerbotPipeline:
    def process_item(self, item, spider):
        return item

class CollectItemsPipeline:
    def __init__(self):
        self.items = []

    def open_spider(self, spider):
        print("CollectItemsPipeline: Spider opened")

    def process_item(self, item, spider):
        print(f"CollectItemsPipeline: Processing item: {item}")
        self.items.append(item)
        return item

    def close_spider(self, spider):
        # Store items for access in main.py
        print(f"CollectItemsPipeline: Closing spider, collected {len(self.items)} items")
        spider.collected_items = self.items