from bs4 import BeautifulSoup
import urllib2
import re
import pprint
import json

url = "http://www.brianbondy.com/stackexchange-twitter/stackoverflow/"
file_naem = 'twitter_stack_link'

soup = BeautifulSoup(urllib2.urlopen(url))
for item in soup.find(id="mainContent").find_all('li'):
    twitter_url = item.find(href=re.compile('twitter'))
    stack_overflow = item.find(href=re.compile('stackoverflow'))
    user = dict(stack_username=stack_overflow.string, stack_url=stack_overflow['href'],\
            twitter_username=twitter_url.string, twitter_url=twitter_url['href'])
    user = json.dumps(user)
    print user
