import webbrowser
import time

from twitter.api import Twitter
from twitter.oauth import OAuth, write_token_file
from twitter.oauth_dance import oauth_dance

ARCHIEVER_CONSUMER_KEY = 'd8hIyfzs7ievqeeZLjZrqQ'
ARCHIEVER_CONSUMER_SECRET = 'AnZmK0rnvaX7BoJ75l6XlilnbyMv7FoiDXWVmPD8'

FOLLOWING_CONSUMER_KEY = 'USRZQfvFFjB6UvZIN2Edww'
FOLLOWING_CONSUMER_SECRET = 'AwGAaSzZa5r0TDL8RKCDtffnI9H9mooZUdOa95nw8'

def generate_archiever_token():
    oauth_token, oauth_token_secret =  oauth_dance("Twitter-Archiver",
            ARCHIEVER_CONSUMER_KEY,ARCHIEVER_CONSUMER_SECRET)
    auth_file = open('./auth_users', 'a')
    auth_file.write('%s %s\n' % (oauth_token, oauth_token_secret))
    auth_file.close()
    return

def generate_following_token():
    oauth_token, oauth_token_secret = oauth_dance("Twitter-Follow",
            FOLLOWING_CONSUMER_KEY, FOLLOWING_CONSUMER_SECRET)
    auth_file = open('./auth_users_follow', 'a')
    auth_file.write('%s %s\n' % (oauth_token, oauth_token_secret))
    auth_file.close()
    return

def main():
    while True:
        generate_archiever_token()
        generate_following_token()
        a = input()

if __name__ == '__main__':
    main()
