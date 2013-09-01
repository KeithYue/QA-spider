from scrapy.spider import BaseSpider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from qa_sns_spider.items import YahooAnswer, YahooUser, YahooQuestion
from scrapy.contrib.loader import XPathItemLoader
from scrapy import log
from urlparse import urlparse, parse_qs
from scrapy.contrib.loader.processor import MapCompose, Join, TakeFirst
from scrapy.utils.markup import remove_entities
import time
import re

class YahooSpider(CrawlSpider):
    name = 'answers.yahoo.com'
    allowed_domains = ['answers.yahoo.com']
    start_urls = [
            'http://answers.yahoo.com/dir/index',
            ]
    rules = (
            Rule(SgmlLinkExtractor(allow = (r'http://answers\.yahoo\.com/dir/index\?(sid=\d+)',), unique = True)),
            Rule(SgmlLinkExtractor(allow = (r'http://answers\.yahoo\.com/question/index\?(qid=.+)'), unique = True), callback = 'parse_question_page'),
        )

    question_xpath = '//div[@id="yan-question"]'
    answer_xpath = '//div[@id="yan-answers"]'
    best_answer_xpath = '//div[@class="answer best"]'
    category_xpath = '//ol[@id="yan-breadcrumbs"]'

    def parse_question_page(self,response):
        hxs = HtmlXPathSelector(response)
        question_loader = XPathItemLoader(item = YahooQuestion(), selector = hxs)
        answers_loader = XPathItemLoader(item = YahooAnswer(), selector = hxs)
# get question id
        question_loader.add_value('question_id',''.join(parse_qs(urlparse(response.request.url).query)['qid']))
# print question_loader.get_output_value('question_id')

# get question title
        question_loader.add_xpath('question_title',self.question_xpath+'//h1[contains(@class, "subject")]/text()')

# get question content
        question_loader.add_xpath('question_content',self.question_xpath+'//div[contains(@class, "content")]/text()')

# get question status
        question_loader.add_xpath('status',self.question_xpath+'//div[@class="hd"]//h2/text()')

#get question url
        question_loader.add_value('question_url',''.join([
            'http://answers.yahoo.com/question/index?qid=',
            question_loader.get_output_value('question_id')
            ]))
#get question date
        question_loader.add_xpath('asking_date',''.join([
            self.question_xpath,
            '//div[@class="qa-container"]//ul[@class="meta"]',
            '/li[1]/abbr/@title'
            ]))
#import date
        question_loader.add_value('import_date',time.strftime("%Y-%m-%d %A %X %Z", time.localtime()))

# asking user
        question_loader.add_value('asker', self.get_user(hxs.select(''.join([
            self.question_xpath,
            ]))))

# interestin marks
        question_loader.add_xpath('number_of_interesting_marks', ''.join([
            '//ul[@id="yan-question-tools"]',
            '//li[@id="yan-starthis"]',
            '//span[contains(@class,"star-count")]/text()'
            ]))
# number of answers
        question_loader.add_xpath('number_of_answers',''.join([
            self.answer_xpath,
            '/div[@class="hd"]',
            '/h3/text()'
            ]))
#begin to parse answers

# category of the question item
        question_loader.add_xpath('category',''.join([self.category_xpath, '//li//a//text()']))
# best answer
        best_answer_selector = hxs.select(self.best_answer_xpath)

        if best_answer_selector:
            yield self.get_answer(best_answer_selector, question_loader)

#other answers
        for ans_selector in hxs.select(self.answer_xpath).select('.//li/div[@class="answer"]'):
            # self.get_answer(ans_selector, question_loader)
            yield self.get_answer(ans_selector, question_loader)

        yield question_loader.load_item()

    def get_user(self, selector):
        user_loader = XPathItemLoader(item = YahooUser(), selector = selector)
        user_loader.add_xpath('user_name', './/span[contains(@class, "user")]//span[contains(@class, "fn")]/text()')
        user_loader.add_xpath('user_url', './/span[@class="user"]//a[@class="url"]/@href')
        user_loader.add_value('user_id', re.match(r'http://answers\.yahoo\.com/my/profile\?show=(.*)',
            user_loader.get_output_value('user_url')
            ).group(1))

        if user_loader.get_collected_values('user_name'):
            return user_loader.load_item()
        else:
            return None

    def get_answer(self, selector, question_loader):
        answer_loader = XPathItemLoader(item = YahooAnswer(), selector = selector)
        answer_loader.add_xpath('answer_id', './@id')
        answer_loader.add_xpath('answer_content','.//div[@class="qa-container"]//div[@class="content"]//text()')
        answer_loader.add_value('answerer',self.get_user(selector))
        answer_loader.add_value('question_id',question_loader.get_output_value('question_id'))
        answer_loader.add_xpath('answering_date',''.join([
            './/div[@class="qa-container"]//ul[@class="meta"]',
            '/li[1]/abbr/@title'
            ]))
        answer_loader.add_xpath('marks',''.join([
            './/div[@class="utils-container"]',
            '//li[@class="rate-up"]',
            '//span[@class="seo-rated"]/text()'
            ]))
        answer_loader.add_xpath('marks',''.join([
            './/div[@class="utils-container"]',
            '//li[@class="rate-up"]',
            '//span[@class="seo-rated"]//strong/text()'
            ]))
# get the good number ot bad number
        marks = answer_loader.get_output_value('marks')
        print marks
        if marks.find('good'):
            answer_loader.add_value('number_of_good_marks', marks.split(' ')[0])
#bad numbers
# is best answer
        answer_class = selector.select('./@class').extract()[0]
        if answer_class.find('best') != -1:
            answer_loader.add_value('is_best_answer', 1)
        else:
            answer_loader.add_value('is_best_answer', 0)

        return answer_loader.load_item()










