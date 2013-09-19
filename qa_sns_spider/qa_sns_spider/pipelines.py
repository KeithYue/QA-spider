# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.contrib.exporter import JsonLinesItemExporter
from qa_sns_spider.items import YahooAnswer, YahooUser, YahooQuestion
from qa_sns_spider.spiders.lazytweet import LazytweetSpider
from qa_sns_spider.spiders.yahoo_answer import YahooSpider

class QaSnsSpiderPipeline(object):
    def process_item(self, item, spider):
        return item


class YahooExportPipeline(object):

    def __init__(self):
#different item is dispatched to different files
        self.files = {}
        self.exporter = {}
        print 'pipeline init'

    def open_spider(self, spider):
        print 'open spider'

        self.files['question'] = open(''.join([
            'data/',
            spider.name,
            '_questions',
            '.json'
            ]), 'a+b')

        self.files['answer'] = open(''.join([
            'data/',
            spider.name,
            '_answers',
            '.json'
            ]), 'a+b')

        self.exporter['question'] = JsonLinesItemExporter(self.files['question'])
        self.exporter['answer'] = JsonLinesItemExporter(self.files['answer'])
        for exporter in self.exporter.itervalues():
            exporter.start_exporting()

    def close_spider(self, spider):
        print 'close spider'
        for exporter in self.exporter.itervalues():
            exporter.finish_exporting()
        for f in self.files.itervalues():
            f.close()
#remove all file in the pipeline
        self.files.clear()

    def process_item(self, item, spider):
        # print type(spider), isinstance(spider, LazytweetSpider)
        # print item.__class__.__name__
        if item.__class__.__name__.lower().find('question') != -1:
            self.exporter['question'].export_item(item)
        elif item.__class__.__name__.lower().find('answer') != -1:
            self.exporter['answer'].export_item(item)
        else:
            pass

        return item
