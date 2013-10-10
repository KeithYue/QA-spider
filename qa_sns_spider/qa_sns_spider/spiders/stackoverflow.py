from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from qa_sns_spider.items import StackOverflowAnswer, StackOverflowUser, StackOverflowQuestion
from scrapy.contrib.loader import XPathItemLoader
import json
import re

# simply assume that the commands are run in sns directory
def get_stack_urls():
    start_urls = []
    link_file = open('./data/stack_twitter_link.json')
    for data in link_file.readlines():
        stack_url = json.loads(data).get('stack_url')
        start_urls.append(stack_url)
    return start_urls

class StackoverflowSpider(CrawlSpider):
    name = 'stackoverflow'
    allowed_domains = ['stackoverflow.com']
    start_urls = get_stack_urls()

    rules = (
        Rule(SgmlLinkExtractor(allow=r'(.*)\?tab=answers(.*)'), callback='parse_item', follow=True),
        Rule(SgmlLinkExtractor(allow=r'/questions/'), callback='parse_question', follow = False),
    )

    question_xpath = "//div[@id='question']"
    answers_xpath = "//div[@id='answers']//div[@data-answerid]"

    def parse_item(self, response):
        pass

    def parse_question(self, response):
        # print 'I am parsing question'
        hxs = HtmlXPathSelector(response)
        for question_selector in hxs.select(self.question_xpath):
            self.get_question(question_selector, response)

        for answer_selector in hxs.select(self.answers_xpath):
            self.get_answer(answer_selector, response)


    # label can be 'question' or 'answer'
    def get_user(self, selector, response, label):
        user_loader = XPathItemLoader(item = StackOverflowUser(),
                selector = selector)
        user_loader.add_xpath('user_name', ''.join([
            './/div[contains(@class, "user-details")]',
            '/a/text()'
            ]))
        user_loader.add_xpath('user_link', ''.join([
            './/div[contains(@class, "user-details")]',
            '/a/@href'
            ]))
        user_loader.add_value('user_id',
                user_loader.get_output_value('user_link'))

        # print user_loader.get_output_value('user_id')

        return

    def get_question(self, selector, response):
        hxs = HtmlXPathSelector(response)
        number_of_answers = hxs.select(''.join([
            '//div[@id="answers"]',
            '//div[contains(@class, "answers-subheader")]',
            '/h2/text()'
            ])).extract()

        question_loader = XPathItemLoader(item = StackOverflowQuestion(),
                selector = selector)
        question_loader.add_xpath('question_content', ''.join([
            ".//td[@class='postcell']",
            "//div[@class='post-text']/p/text()"
            ]))
        question_loader.add_xpath('question_tags', ''.join([
            ".//div[@class='post-taglist']",
            "//a[@class='post-tag']/text()"
            ]))
        question_loader.add_xpath('question_id', ''.join([
            './@data-questionid'
            ]))
        question_loader.add_xpath('marks', ''.join([
            ".//span[contains(@class, 'vote-count-post')]/text()"
            ]))
        question_loader.add_value('asker', self.get_user(selector, response, 'question'))
        question_loader.add_value('number_of_answers',
                int(number_of_answers[0].strip().split(' ')[0]))

        print question_loader.get_output_value('number_of_answers')

        return

    def get_answer(self, selector, response):
        answer_loader = XPathItemLoader(item = StackOverflowAnswer(),
                selector = selector)
        answer_loader.add_xpath('answer_content', ''.join([
            ".//td[@class='answercell']/div[@class='post-text']",
            "/p/text()"
            ]))
        answer_loader.add_xpath('answer_id', ''.join([
            "./@data-answerid"
            ]))
        answer_loader.add_xpath('marks', ''.join([
            ".//span[contains(@class, 'vote-count-post')]/text()"
            ]))
        # is best answer?
        if selector.select('./@class').extract()[0].find('accepted-answer') != -1:
            answer_loader.add_value('is_best_answer', 1)
        else:
            answer_loader.add_value('is_best_answer', 0)
        # get user name
        answer_loader.add_value('answerer', self.get_user(selector, response, 'answer'))

        # print answer_loader.get_output_value('marks')

        return
