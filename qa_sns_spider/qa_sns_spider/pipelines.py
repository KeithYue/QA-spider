# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.contrib.exporter import JsonLinesItemExporter
from qa_sns_spider.items import YahooAnswer, YahooUser, YahooQuestion
class QaSnsSpiderPipeline(object):
    def process_item(self, item, spider):
        return item

class YahooExportPipeline(object):

    def __init__(self):
#different item is dispatched to different files
        self.files = {}
        self.exporter = {}

    def open_spider(self, spider):
        print 'open spider'
        self.files['question'] = open('question.json','w+b')
        self.files['answer'] = open('answer.json', 'w+b')
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
        if type(item) is YahooQuestion:
            print 'question'
            self.exporter['question'].export_item(item)
        elif type(item) is YahooAnswer:
            print 'answer'
            self.exporter['answer'].export_item(item)
        return item
