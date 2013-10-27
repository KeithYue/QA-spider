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
        print twitter_name


main()
