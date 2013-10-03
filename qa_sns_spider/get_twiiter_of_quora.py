# coding=utf-8
from bs4 import BeautifulSoup
import urllib2
import re
from sys import argv
import json
import os
from twitter import Twitter, OAuth

# init twitter
from twitter.api import Twitter, TwitterError
from twitter.oauth import OAuth, read_token_file
from twitter.oauth_dance import oauth_dance
from twitter.auth import NoAuth
from twitter.util import Fail, err, expand_line, parse_host_list
from twitter.follow import lookup

CONSUMER_KEY='XLVBlYhYqJNAPPD5OEQ'
CONSUMER_SECRET='EUDfuBcgB37Dn34Vo6tSaKcBKQESQOW1M6PIMQ'
oauth_filename = (os.getenv("HOME", "") + os.sep
                  + ".twitter-archiver_oauth")

oauth_token, oauth_token_secret = read_token_file(oauth_filename)
auth = OAuth(oauth_token, oauth_token_secret, CONSUMER_KEY,
             CONSUMER_SECRET)

t = Twitter(auth=auth, api_version='1.1', domain='api.twitter.com')
# print twitter.statuses.home_timeline()
# the input is a quora profile page, and we return the twitter username
def get_quora_twitter_user_name(url):
    soup = BeautifulSoup(urllib2.urlopen(url))
    for link in soup.find_all('a'):
        address = link.get('href')
        if re.match(r'http://twitter.com/', address):
            return  address.split('/')[-1]

# quora link file
link_file = open(argv[1])

def main():
    for link in link_file.readlines():
        twitter_name = get_quora_twitter_user_name(link)
        get_tweets(twitter_name)
        get_following_information(twitter_name)

def get_tweets(twitter_name):
    os.system('./archiver_beta1.py -o %s -s %s' % (twitter_name, './data/tweets/'))

def get_following_information(twitter_name):
    if twitter_name not in os.listdir('./data/twitter-follow/'):
        os.system('./follow.py -o -g -i %s > ./data/twitter-follow/%s' % (twitter_name, twitter_name))
    else:
        print '%s\'s following information  has already been archieved!!' % twitter_name

main()
