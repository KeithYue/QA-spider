#! /usr/bin/python
"""USAGE
    twitter-archiver [options] <-|user> [<user> ...]

DESCRIPTION
    Archive tweets of users, sorted by date from oldest to newest, in
    the following format: <id> <date> <<screen_name>> <tweet_text>
    Date format is: YYYY-MM-DD HH:MM:SS TZ. Tweet <id> is used to
    resume archiving on next run. Archive file name is the user name.
    Provide "-" instead of users to read users from standard input.

OPTIONS
 -o --oauth            authenticate to Twitter using OAuth (default: no)
 -s --save-dir <path>  directory to save archives (default: current dir)
 -a --api-rate         see current API rate limit status
 -t --timeline <file>  archive own timeline into given file name (requires
                       OAuth, max 800 statuses)
 -m --mentions <file>  archive own mentions instead of timeline into
                       given file name (requires OAuth, max 800 statuses)
 -v --favorites        archive user's favorites instead of timeline
 -f --follow-redirects follow redirects of urls
 -r --redirect-sites   follow redirects for this comma separated list of hosts
 -d --dms <file>       archive own direct messages (both received and
                       sent) into given file name.
 -i --isoformat        store dates in ISO format (specifically RFC 3339)

AUTHENTICATION
    Authenticate to Twitter using OAuth to archive tweets of private profiles
    and have higher API rate limits. OAuth authentication tokens are stored
    in ~/.twitter-archiver_oauth.
"""

from __future__ import print_function

import os, sys, time as _time, calendar, functools
from datetime import time, date, datetime
from getopt import gnu_getopt as getopt, GetoptError

try:
    import urllib.request as urllib2
    import http.client as httplib
except ImportError:
    import urllib2
    import httplib


# T-Archiver (Twitter-Archiver) application registered by @stalkr_
CONSUMER_KEY='d8hIyfzs7ievqeeZLjZrqQ'
CONSUMER_SECRET='AnZmK0rnvaX7BoJ75l6XlilnbyMv7FoiDXWVmPD8'

from twitter.api import Twitter, TwitterError
from twitter.oauth import OAuth, read_token_file
from twitter.oauth_dance import oauth_dance
from twitter.auth import NoAuth
from twitter.util import Fail, err, expand_line, parse_host_list
from twitter.follow import lookup
from twitter.timezones import utc as UTC, Local
import json
import random

def get_auths_data():
    auth_file = open('./auth_users.json', 'r')
    auth_users = []
    for auther in auth_file.readlines():
        auth_users.append(auther.strip().split(r' '))
    return auth_users

def parse_args(args, options):
    """Parse arguments from command-line to set options."""
    long_opts = ['help', 'oauth', 'save-dir=', 'api-rate', 'timeline=', 'mentions=', 'favorites', 'follow-redirects',"redirect-sites=", 'dms=', 'isoformat']
    short_opts = "hos:at:m:vfr:d:i"
    opts, extra_args = getopt(args, short_opts, long_opts)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(__doc__)
            raise SystemExit(0)
        elif opt in ('-o', '--oauth'):
            options['oauth'] = True
        elif opt in ('-s', '--save-dir'):
            options['save-dir'] = arg
        elif opt in ('-a', '--api-rate'):
            options['api-rate' ] = True
        elif opt in ('-t', '--timeline'):
            options['timeline'] = arg
        elif opt in ('-m', '--mentions'):
            options['mentions'] = arg
        elif opt in ('-v', '--favorites'):
            options['favorites'] = True
        elif opt in ('-f', '--follow-redirects'):
            options['follow-redirects'] = True
        elif opt in ('-r', '--redirect-sites'):
            options['redirect-sites'] = arg
        elif opt in ('-d', '--dms'):
            options['dms'] = arg
        elif opt in ('-i', '--isoformat'):
            options['isoformat'] = True

    options['extra_args'] = extra_args

def load_tweets(filename):
    """Load tweets from file into dict, see save_tweets()."""
    try:
        archive = open(filename,"r")
    except IOError: # no archive (yet)
        return {}

    tweets = {}
#first line of the file is the twitter name information
    for line in archive.readlines()[1:]:
        tid, text = line.strip().split(" ", 1)
        tweets[int(tid)] = text.decode("utf-8")

    archive.close()
    return tweets

def save_tweets(filename, tweets, user_id):
    """Save tweets from dict to file.

    Save tweets from dict to UTF-8 encoded file, one per line:
        <tweet id (number)> <tweet text>
    Tweet text is:
        <date> <<user>> [RT @<user>: ]<text>

    Args:
        filename: A string representing the file name to save tweets to.
        tweets: A dict mapping tweet-ids (int) to tweet text (str).
    """
    if len(tweets) == 0:
        return

    try:
        archive = open(filename,"w")
    except IOError as e:
        err("Cannot save tweets: %s" % str(e))
        return

#first line is for user_id and #tweet
    archive.write(''.join([
        '%d' % user_id,
        '\t',
        '#tweets\n'
        ]))
    for k in sorted(tweets.keys()):
        archive.write("%i %s\n" % (k, tweets[k].encode('utf-8')))

    archive.close()

def format_date(utc, isoformat=False):
    """Parse Twitter's UTC date into UTC or local time."""
    u = datetime.strptime(utc.replace('+0000','UTC'), '%a %b %d %H:%M:%S %Z %Y')
    # This is the least painful way I could find to create a non-naive
    # datetime including a UTC timezone. Alternative suggestions
    # welcome.
    unew = datetime.combine(u.date(), time(u.time().hour,
        u.time().minute, u.time().second, tzinfo=UTC))

    # Convert to localtime
    unew = unew.astimezone(Local)

    if isoformat:
        return unew.isoformat()
    else:
        return unew.strftime('%Y-%m-%d %H:%M:%S %Z')

def expand_format_text(hosts, text):
    """Following redirects in links."""
    return direct_format_text(expand_line(text, hosts))

def direct_format_text(text):
    """Transform special chars in text to have only one line."""
    return text.replace('\n','\\n').replace('\r','\\r')

def statuses_resolve_uids(twitter, tl):
    """Resolve user ids to screen names from statuses."""
    # get all user ids that needs a lookup (no screen_name key)
    user_ids = []
    for t in tl:
        rt = t.get('retweeted_status')
        if rt and not rt['user'].get('screen_name'):
            user_ids.append(rt['user']['id'])
        if not t['user'].get('screen_name'):
            user_ids.append(t['user']['id'])

    # resolve all of them at once
    names = lookup(twitter, list(set(user_ids)))

    # build new statuses with resolved uids
    new_tl = []
    for t in tl:
        rt = t.get('retweeted_status')
        if rt and not rt['user'].get('screen_name'):
            name = names[rt['user']['id']]
            t['retweeted_status']['user']['screen_name'] = name
        if not t['user'].get('screen_name'):
            name = names[t['user']['id']]
            t['user']['screen_name'] = name
        new_tl.append(t)

    return new_tl

def statuses_portion(twitter, screen_name, max_id=None, mentions=False, favorites=False, received_dms=None, isoformat=False):
    """Get a portion of the statuses of a screen name."""
    kwargs = dict(count=200, include_rts=1, screen_name=screen_name)
    if max_id:
        kwargs['max_id'] = max_id

    tweets = {}
    if mentions:
        tl = twitter.statuses.mentions_timeline(**kwargs)
    elif favorites:
        tl = twitter.favorites.list(**kwargs)
    elif received_dms != None:
        if received_dms:
            tl = twitter.direct_messages(**kwargs)
        else: # sent DMs
            tl = twitter.direct_messages.sent(**kwargs)
    else: # timeline
        if screen_name:
            tl = twitter.statuses.user_timeline(**kwargs)
        else: # self
            tl = twitter.statuses.home_timeline(**kwargs)

    # some tweets do not provide screen name but user id, resolve those
    # this isn't a valid operation for DMs, so special-case them
    if received_dms == None:
      newtl = statuses_resolve_uids(twitter, tl)
    else:
      newtl = tl
    for t in newtl:
        text = t['text']
        rt = t.get('retweeted_status')
        if rt:
            text = "RT @%s: %s" % (rt['user']['screen_name'], rt['text'])
        # DMs don't include mentions by default, so in order to show who
        # the recipient was, we synthesise a mention. If we're not
        # operating on DMs, behave as normal
        if received_dms == None:
          tweets[t['id']] = "%s <%s> %s" % (format_date(t['created_at'], isoformat=isoformat),
                                            t['user']['screen_name'],
                                            format_text(text))
        else:
          tweets[t['id']] = "%s <%s> @%s %s" % (format_date(t['created_at'], isoformat=isoformat),
                                            t['sender_screen_name'],
                                            t['recipient']['screen_name'],
                                            format_text(text))
    return tweets

def statuses(twitter, screen_name, tweets, mentions=False, favorites=False, received_dms=None, isoformat=False):
    """Get all the statuses for a screen name."""
    max_id = None
    fail = Fail()
    # get portions of statuses, incrementing max id until no new tweets appear
    while True:
        try:
            portion = statuses_portion(twitter, screen_name, max_id, mentions, favorites, received_dms, isoformat)
        except TwitterError as e:
            if e.e.code == 401:
                err("Fail: %i Unauthorized (tweets of that user are protected)"
                    % e.e.code)
                break
            elif e.e.code == 400:
                err("Fail: %i API rate limit exceeded" % e.e.code)
                rate = twitter.account.rate_limit_status()
                reset = rate['reset_time_in_seconds']
                reset = time.asctime(time.localtime(reset))
                delay = int(rate['reset_time_in_seconds']
                            - time.time()) + 5 # avoid race
                err("Hourly limit of %i requests reached, next reset on %s: "
                    "going to sleep for %i secs" % (rate['hourly_limit'],
                                                    reset, delay))
                fail.wait(delay)
                continue
            elif e.e.code == 404:
                err("Fail: %i This profile does not exist" % e.e.code)
                break
            elif e.e.code == 502:
                err("Fail: %i Service currently unavailable, retrying..."
                    % e.e.code)
            else:
                err("Fail: %s\nRetrying..." % str(e)[:500])
            fail.wait(3)
        except urllib2.URLError as e:
            err("Fail: urllib2.URLError %s - Retrying..." % str(e))
            fail.wait(3)
        except httplib.error as e:
            err("Fail: httplib.error %s - Retrying..." % str(e))
            fail.wait(3)
        except KeyError as e:
            err("Fail: KeyError %s - Retrying..." % str(e))
            fail.wait(3)
        else:
            new = -len(tweets)
            tweets.update(portion)
            new += len(tweets)
            err("Browsing %s statuses, new tweets: %i"
                % (screen_name if screen_name else "home", new))
            if new < 190:
                break
            max_id = min(portion.keys())-1 # browse backwards
            fail = Fail()

def rate_limit_status(twitter):
    """Print current Twitter API rate limit status."""
    r = twitter.account.rate_limit_status()
    print("Remaining API requests: %i/%i (hourly limit)"
          % (r['remaining_hits'], r['hourly_limit']))
    print("Next reset in %is (%s)"
          % (int(r['reset_time_in_seconds'] - time.time()),
             time.asctime(time.localtime(r['reset_time_in_seconds']))))

def main(args=sys.argv[1:]):
    options = {
        'oauth': False,
        'save-dir': ".",
        'api-rate': False,
        'timeline': "",
        'mentions': "",
        'dms': "",
        'favorites': False,
        'follow-redirects': False,
        'redirect-sites': None,
        'isoformat': False,
    }
    try:
        parse_args(args, options)
    except GetoptError as e:
        err("I can't do that, %s." % e)
        raise SystemExit(1)

    # exit if no user given
    # except if asking for API rate, or archive of timeline or mentions
    if not options['extra_args'] and not (options['api-rate'] or
                                          options['timeline'] or
                                          options['mentions'] or
                                          options['dms']):
        print(__doc__)
        return

    # authenticate using OAuth, asking for token if necessary
    if options['oauth']:
        # oauth_filename = (os.getenv("HOME", "") + os.sep
        #                   + ".twitter-archiver_oauth")
        # if not os.path.exists(oauth_filename):
        #     oauth_dance("Twitter-Archiver", CONSUMER_KEY, CONSUMER_SECRET,
        #                 oauth_filename)
        # oauth_token, oauth_token_secret = read_token_file(oauth_filename)
        auths = get_auths_data()
        random_index = random.randint(0, len(auths) - 1)
        print(random_index)
        auth = OAuth(auths[random_index][0], auths[random_index][1], CONSUMER_KEY,
                     CONSUMER_SECRET)
    else:
        auth = NoAuth()

    twitter = Twitter(auth=auth, api_version='1.1', domain='api.twitter.com')

    if options['api-rate']:
        rate_limit_status(twitter)
        return

    global format_text
    if options['follow-redirects'] or options['redirect-sites'] :
        if options['redirect-sites']:
            hosts = parse_host_list(options['redirect-sites'])
        else:
            hosts = None
        format_text = functools.partial(expand_format_text, hosts)
    else:
        format_text = direct_format_text

    # read users from command-line or stdin
    users = options['extra_args']
    if len(users) == 1 and users[0] == "-":
        users = [line.strip() for line in sys.stdin.readlines()]

    # save tweets for every user
    total, total_new = 0, 0
    for user in users:
        filename = options['save-dir'] + os.sep + user
        user_id = twitter.users.lookup(screen_name=user)[0]['id']
        # print('%d\n' % user_id)
        if options['favorites']:
            filename = filename + "-favorites"
        print("* Archiving %s tweets in %s" % (user, filename))

        tweets = {}
        try:
            tweets = load_tweets(filename)
        except Exception as e:
            err("Error when loading saved tweets: %s - continuing without"
                % str(e))

        new = 0
        before = len(tweets)
        try:
            statuses(twitter, user, tweets, options['mentions'], options['favorites'], isoformat=options['isoformat'])
        except KeyboardInterrupt:
            err()
            err("Interrupted")
            raise SystemExit(1)

        save_tweets(filename, tweets, user_id)
        total += len(tweets)
        new = len(tweets) - before
        total_new += new
        print("Total tweets for %s: %i (%i new)" % (user, len(tweets), new))

    print("Total: %i tweets (%i new) for %i users"
          % (total, total_new, len(users)))

# run as a exe script
if __name__ == '__main__':
    main()

