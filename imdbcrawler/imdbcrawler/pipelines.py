# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json

class ImdbcrawlerPipeline:
    def process_item(self, item, spider):
        return item


# This pipeline overwrites the produced json file each time the command to run the spider is executed
class OverWriteFilePipeline:
    def open_spider(self, spider):
        # Open files in write mode to overwrite existing files
        self.json_file = open('imdb_data.json', 'w', encoding='utf-8')
       
    def close_spider(self, spider):
        self.json_file.close()

    def process_item(self, item, spider):
        return item