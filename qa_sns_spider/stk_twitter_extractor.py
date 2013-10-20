from bs4 import BeautifulSoup
import sys
import json
import urllib2
import re
import time
from get_tweets_multi_thread import TwitterSpider
from get_following_multi_thread import FollowingSpider
# input: stack_overflow answers file
# output: the link between stk users and twitter users

# argv[1]: stack_over_flow file name
answer_file = open('./data/stackoverflow_answers.json', 'r')
stk_twitter_link_file = open('./data/stk_twitter_link', 'w')
for line in answer_file.xreadlines():
    answer = json.loads(line.strip())
    answerer = answer['answerer']
    # print answerer.get('user_name')
    # print answerer['user_link']
    if answerer.get('user_link'):
        profile_url = ''.join([
            'http://stackoverflow.com',
            answerer['user_link']
            ])
        soup = BeautifulSoup(urllib2.urlopen(profile_url))
        twitter_link = None
        if soup.find_all(href = re.compile('twitter')):
            twitter_link = soup.find_all(href = re.compile('twitter'))[0]
            twitter_url = twitter_link['href']
            twitter_user_name = unicode(twitter_link.string)
            stk_user_name = answerer.get('user_name')
            stk_user_id = int(answerer.get('user_id').split('/')[2])
            link_obj = {
                    'twitter_name': twitter_user_name,
                    'twitter_url': twitter_url,
                    'stk_user_name': stk_user_name,
                    'stk_user_id': stk_user_id
                    }
            # write this link to file
            json_link_obj = json.dumps(link_obj)
            print json_link_obj
            stk_twitter_link_file.write(''.join([
                json_link_obj,
                '\n'
                ]))
            stk_twitter_link_file.flush()
            # crawl the tweets
            ts = TwitterSpider(twitter_url.split('/')[-1])
            ts.start()
            # crawl the following information
            fs = FollowingSpider(twitter_url.split('/')[-1])
            fs.start()

stk_twitter_link_file.close()

