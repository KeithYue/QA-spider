from threading import Thread, Lock
from archiver_beta1 import *
import os
import json

# T-Archiver (Twitter-Archiver) application registered by @stalkr_
CONSUMER_KEY = 'd8hIyfzs7ievqeeZLjZrqQ'
CONSUMER_SECRET = 'AnZmK0rnvaX7BoJ75l6XlilnbyMv7FoiDXWVmPD8'


# load auth file
auth_users = get_auths_data()
auth_pointer = 0

AUTH_LOCK = Lock()

# user tweets need to be crawled
users_list = []

# load all user
def load_user_list(filename):
    global users_list
    for line in open(filename).readlines():
        item = json.loads(line.strip())
        users_list.append(item['twitter_username'][1:])

class TwitterSpider(Thread):
    def __init__(self, twitter_username):
        super(TwitterSpider, self).__init__()
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
        filename = './data/tweets/' + os.sep + \
                self.twitter_username
        user_id = twitter.users.lookup(screen_name=self.twitter_username)[0]['id']
        total, total_new = 0, 0
        tweets = {}
        try:
            tweets = load_tweets(filename)
        except Exception as e:
            err("Error when loading saved tweets: %s - continuing without"
                % str(e))

        new = 0
        before = len(tweets)
        try:
            statuses(twitter, self.twitter_username, tweets)
        except KeyboardInterrupt:
            err()
            err("Interrupted")
            raise SystemExit(1)

        save_tweets(filename, tweets, user_id)
        total += len(tweets)
        new = len(tweets) - before
        total_new += new
        print("Total tweets for %s: %i (%i new)" % (self.twitter_username,
            len(tweets), new))

def get_tweets(thread_number = 5):
    total_number = len(users_list)
    index = 0
    while index < total_number:
        thread_list = []
        for i in range(0, thread_number):
            if index < total_number:
                thread_list.append(TwitterSpider(users_list[index]))
                index += 1
        for spider in thread_list:
            spider.start()
        for spider in thread_list:
            spider.join()


if __name__ == '__main__':
    load_user_list('./data/stack_twitter_link.json')
    get_tweets()
