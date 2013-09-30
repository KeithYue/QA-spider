#! /usr/bin/python
# coding=utf-8

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
# if not os.path.exists(oauth_filename):
#     oauth_dance("Twitter-Archiver", CONSUMER_KEY, CONSUMER_SECRET,
#                 oauth_filename)
oauth_token, oauth_token_secret = read_token_file(oauth_filename)
auth = OAuth(oauth_token, oauth_token_secret, CONSUMER_KEY,
             CONSUMER_SECRET)

t = Twitter(auth=auth, api_version='1.1', domain='api.twitter.com')
# print twitter.statuses.home_timeline()

print argv[1]

# read the file

def main():
    json_file = open(argv[1])
    for line in json_file.readlines():
        item = json.loads(line)
        if item.has_key('asker'):
            twitter_name = item['asker']['twitter_username']
        if item.has_key('answerer'):
            twitter_name  = item['answerer']['twitter_username']
        os.system('./archiver_beta1.py -o %s -s %s' % (twitter_name, './data/tweets/'))
        if twitter_name not in os.listdir('./data/twitter-follow/'):
            os.system('./follow.py -o -g -i %s > ./data/twitter-follow/%s' % (twitter_name, twitter_name))
        else:
            print '%s\'s following information  has already been archieved!!' % twitter_name

def test():
    twitter_name = argv[1]
    os.system('./archiver_beta1.py -o %s -s %s' % (twitter_name, './data/tweets/'))
    if twitter_name not in os.listdir('./data/twitter-follow/'):
        os.system('./follow.py -o -g -i %s > ./data/twitter-follow/%s' % (twitter_name, twitter_name))
    else:
        print '%s\'s following information  has already been archieved!!' % twitter_name

main()
