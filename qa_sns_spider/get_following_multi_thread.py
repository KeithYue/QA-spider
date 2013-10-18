from threading import Thread, Lock
from follow_beta1 import *
import os
import json


def load_auths():
    auth_file = open('./auth_users_follow', 'r')
    auth_users = []
    for auther in auth_file.readlines():
        auth_users.append(auther.strip().split(r' '))
    auth_file.close()
    return auth_users


class FollowingSpider(Thread):
    def __init__(self, twitter_username):
        super(FollowingSpider, self).__init__()
        self.twitter_username = twitter_username

    def run(self):
        global auth_pointer

        # lock the auth pointer for distribution
        AUTH_LOCK.acquire()
        print 'I am starting, using %d auther' % \
                auth_pointer
        auth = OAuth(auth_users[auth_pointer][0],
                auth_users[auth_pointer][1],
                CONSUMER_KEY, CONSUMER_SECRET)
        auth_pointer = (auth_pointer + 1) % len(auth_users)
        AUTH_LOCK.release()

        twitter = Twitter(auth=auth, api_version='1.1',
                domain='api.twitter.com')
        filename = './data/twitter-follow/' + os.sep + \
                self.twitter_username
        follow_file = open(filename, 'w')
        user_ids, users = [], {}
        try:
            user_ids = follow(twitter, self.twitter_username , True)
            users = lookup(twitter, user_ids)
        except KeyboardInterrupt as e:
            err()
            err("Interrupted.")
            raise SystemExit(1)

        for uid in user_ids:
          try:
              follow_file.write('%s\t%s' % (str(uid), users[uid].encode("utf-8")))
              # print(str(uid) + "\t" + users[uid].encode("utf-8"))
          except KeyError:
              pass

def get_following_data(thread_number = 5):
    total_number = len(users_list)
    index = 0
    while index < total_number:
        thread_list = []
        for i in range(0, thread_number):
            if index < total_number:
                thread_list.append(FollowingSpider(users_list[index]))
                index += 1
        for spider in thread_list:
            spider.start()
        for spider in thread_list:
            spider.join()

def load_user_list(filename):
    global users_list
    for line in open(filename).readlines():
        item = json.loads(line.strip())
        users_list.append(item['twitter_username'][1:])

# T-Follow (Twitter-Follow) application registered by @stalkr_
CONSUMER_KEY = 'USRZQfvFFjB6UvZIN2Edww'
CONSUMER_SECRET = 'AwGAaSzZa5r0TDL8RKCDtffnI9H9mooZUdOa95nw8'
auth_users = load_auths()
users_list = []
auth_pointer = 0
AUTH_LOCK = Lock()

if __name__ == '__main__':
    load_user_list('./data/stack_twitter_link.json')
    get_following_data()
