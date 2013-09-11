from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from qa_sns_spider.items import LazyTweetAnswer, LazyTweetQuestion, LazyTweetUser
from scrapy.contrib.loader import XPathItemLoader

class LazytweetSpider(CrawlSpider):
    name = 'lazytweet'
    allowed_domains = ['www.lazytweet.com']
    start_urls = [
            'http://www.lazytweet.com/',
            'http://www.lazytweet.com/unanswered-questions',
            'http://www.lazytweet.com/recent-questions'
            ]

    rules = (
        Rule(SgmlLinkExtractor(allow=r'/\?page=([1-9]*)'), callback='parse_collection_page', follow = True),
        Rule(SgmlLinkExtractor(allow=r'/recent-questions\?page=([1-9]*)'), callback='parse_collection_page', follow = True),
        Rule(SgmlLinkExtractor(allow=r'/unanswered-questions\?page=([1-9]*)'), callback='parse_collection_page', follow = True),
        Rule(SgmlLinkExtractor(allow=r'/post/([1-9]*)'), callback = 'parse_question_page', follow = True),
    )
    question_xpath = '//ul[@class="posts"]/li[@class="hentry"]'
    answers_xpath = '//div[@id="answers"]//div[@class="answer"]'

    def parse_collection_page(self, response):
        pass

    def parse_question_page(self, response):
        hxs = HtmlXPathSelector(response)
        for question_selector in hxs.select(self.question_xpath):
            # question_number += 1
            yield self.get_question(question_selector, response)
        for answer_selector in hxs.select(self.answers_xpath):
            # answers_number += 1
            yield self.get_answer(answer_selector, response)

    def get_user(self, selector):
        user_loader = XPathItemLoader(item = LazyTweetUser(), selector = selector)
        user_loader.add_xpath('twitter_username', ''.join([
            './a[1]/text()'
            ]))
        user_loader.add_value('twitter_url', ''.join([
            r'http://twitter.com/',
            user_loader.get_output_value('twitter_username')
            ]))
        return user_loader.load_item()
        # print user_loader.get_output_value('twitter_url')

    def get_answer(self, selector, response):
        answer_loader = XPathItemLoader(item = LazyTweetAnswer(), \
                selector = selector)
        answer_loader.add_value('question_id', response.url.split('/')[-1])
        answer_loader.add_value('answerer', self.get_user(selector.select(''.join([
            './/span[@class="answer-meta"]'
            ]))))
        answer_loader.add_xpath('answer_content',''.join([
            './/span[@class="answer-body"]',
            '//span[@class="answer-status"]/text()'
            ]))
        return answer_loader.load_item()
        # print answer_loader.get_output_value('answer_content')

    def get_question(self, selector, response):
# both select function and selector's join function need to add dot to search from relative based directory
        question_loader = XPathItemLoader(item = LazyTweetQuestion(), \
                selector = selector)
        question_loader.add_xpath('question_content', ''.join([
            './/span[@class="post-body"]',
            '//span[@class="post-status"]/text()'
            ]))
        question_loader.add_xpath('question_tags', ''.join([
            './/div[@id="post-tags"]//ul/li/a/text()'
            ]))
        question_loader.add_xpath('asking_date', ''.join([
            './/span[@class="post-meta"]//span[@class="timestamp"]/text()'
            ]))
        question_loader.add_value('asker', self.get_user(selector.select(''.join([
            './/span[@class="post-meta"]'
            ]))))
        question_loader.add_xpath('number_of_answers', ''.join([
            './/span[@class="post-meta"]',
            '//a[last()]/text()'
            ]))
        question_loader.add_value('question_id', response.url.split('/')[-1])
        # print question_loader.get_output_value('question_id')
        return question_loader.load_item()
