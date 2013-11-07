from threading import Thread, Lock
from follow_beta1 import *
import os
import json
import Queue
from archiver_beta1 import get_auths_data as archive_auths
import time
import os

def load_auths():
    auth_file = open('./auth_users_follow', 'r')
    auth_users = []
    for auther in auth_file.readlines():
        auth_users.append(auther.strip().split(r' '))
    auth_file.close()
    return auth_users

def get_followed_users():
    'return the user list'
    return os.listdir(''.join([os.curdir,os.sep, 'data',os.sep,'twitter-follow', os.sep]))


class FollowingSpider(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            global auth_pointer # pointer of archiever
            global following_auth_pointer # pointer of following app
            global is_using_archieve

            self.twitter_username = self.queue.get()[1] # get a task
            print 'I am crawling the number %d user!!' % self.queue.get()[0]

            APP_SWITCH.acquire() # get the which app to use
            if(is_using_archieve): # use twitter archiever
                AUTH_LOCK.acquire()
                print 'I am starting, using %d auther' % \
                        auth_pointer
                auth = OAuth(archive_auths_users[auth_pointer][0],
                        archive_auths_users[auth_pointer][1],
                        CONSUMER_KEY, CONSUMER_SECRET)
                auth_pointer = (auth_pointer + 1) % len(archive_auths_users)
                AUTH_LOCK.release()
                is_using_archieve = False
            else: # use twitter following
                FOLLOW_AUTH_LOCK.acquire()
                print 'I am starting, using %d following auth user' % \
                        (following_auth_pointer)
                auth = OAuth(following_auth_users[following_auth_pointer][0],
                        following_auth_users[following_auth_pointer][1],
                        FOLLOW_CONSUMER_KEY,
                        FOLLOW_CONSUMER_SECRET)
                following_auth_pointer = (following_auth_pointer + 1) % len(following_auth_users)
                FOLLOW_AUTH_LOCK.release()
                is_using_archieve = True
            APP_SWITCH.release()

            twitter = Twitter(auth=auth, api_version='1.1',
                    domain='api.twitter.com')
            filename = './data/twitter-follow/' + os.sep + \
                    self.twitter_username
            follow_file = open(filename, 'w')
            user_ids, users = [], {}
            try:
                user_ids = follow(twitter, self.twitter_username , True)
                # HERE we decide not to retrive screen name because it is time-consuming
                # users = lookup(twitter, user_ids)
            except KeyboardInterrupt as e:
                err()
                err("Interrupted.")
                raise SystemExit(1)

            follow_file.write('following twitter id\n')
            for uid in user_ids:
              try:
                  # follow_file.write('%s\t%s\n' % (str(uid), users[uid].encode("utf-8")))
                  follow_file.write('%s\n' % (str(uid)))
                  # print(str(uid) + "\t" + users[uid].encode("utf-8"))
              except KeyError:
                  pass
            follow_file.close()


            time.sleep(70) # to avoid the rate limit, 15 request per 15 mins, differ from tweets

            self.queue.task_done() # indicate the task is finished

def get_following_data(thread_number = 5):
    total_number = len(users_list)
    index = 0
    while index < total_number:
        thread_list = []
        for i in range(0, thread_number):
            if index < total_number:
                thread_list.append(FollowingSpider(users_list[index]))
                print 'Now I am the number %d user!!' % index
                index += 1
        for spider in thread_list:
            spider.start()
        for spider in thread_list:
            spider.join()
        time.sleep(2)

# multi-thread spiders but using a queue to manage all threads
def get_following_data_using_queue():
    total_number = len(users_list)
    # print total_number
    for i in range(max_thead_number): # start total tasks, the number here is the max-size of threads
        t = FollowingSpider(thread_queue)
        t.daemon = True
        t.start()
    for index, user in enumerate(users_list):
        if user not in crawled_users: # dont crawl the crawled users
            thread_queue.put((index, user))
    thread_queue.join()


def load_user_list(filename):
    global users_list
    for line in open(filename).readlines():
        item = json.loads(line.strip())
        users_list.append(item['twitter_username'][1:])

def load_quora_user_list(filename):
    global users_list
    for line in open(filename).xreadlines():
        twitter_id, twitter_username = line.strip().split('\t')
        # print line.strip().split('\t')
        # print twitter_username
        users_list.append(twitter_username)

# T-Archiver (Twitter-Archiver) application registered by @stalkr_
CONSUMER_KEY = 'd8hIyfzs7ievqeeZLjZrqQ'
CONSUMER_SECRET = 'AnZmK0rnvaX7BoJ75l6XlilnbyMv7FoiDXWVmPD8'

# T-Follow (Twitter-Follow) application registered by @stalkr_
FOLLOW_CONSUMER_KEY = 'USRZQfvFFjB6UvZIN2Edww'
FOLLOW_CONSUMER_SECRET = 'AwGAaSzZa5r0TDL8RKCDtffnI9H9mooZUdOa95nw8'

following_auth_users = load_auths()
archive_auths_users = archive_auths()
users_list = []
crawled_users = get_followed_users()
auth_pointer = 0
following_auth_pointer = 0
is_using_archieve = True
AUTH_LOCK = Lock()
FOLLOW_AUTH_LOCK = Lock()
APP_SWITCH = Lock()

# Use queue to set up deamon theads pool

max_thead_number = 60 # every user send request 1/per minute
thread_queue = Queue.Queue(maxsize = max_thead_number)

if __name__ == '__main__':
    load_quora_user_list('./data/quora_id_twitter')
    # print users_list
    # load_user_list('./data/stack_twitter_link.json')
    # get_following_data(thread_number = 8)
    get_following_data_using_queue()
