import tweepy
import os
from scraping import scrape_tweets
import csv
import copy
import json
import uuid
from pprint import pprint
from config import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_SECRET, ACCESS_TOKEN_KEY

TRUMP_SUPPORTER_TWEETS_FOLDER = 'Trump Supporter Tweets'
SANDERS_SUPPORTER_TWEETS_FOLDER = 'Sanders Supporter Tweets'
CRUZ_SUPPORTER_TWEETS_FOLDER = 'Cruz Supporter Tweets'
CLINTON_SUPPORTER_TWEETS_FOLDER = 'Clinton Supporter Tweets'

WORD_COUNT_TWEETS_FOLDER = 'Word Counts'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)

trump_handle = 'realdonaldtrump'
clinton_handle = 'hillaryclinton'
cruz_handle = 'tedcruz'
sanders_handle = 'berniesanders'

candidate_handles = [trump_handle, clinton_handle, cruz_handle, sanders_handle]

trump = api.get_user(trump_handle)
clinton = api.get_user(clinton_handle)
cruz = api.get_user(cruz_handle)
sanders = api.get_user(sanders_handle)

candidates = [trump, clinton, cruz, sanders]

candidate_supporters = {
    trump_handle: 'Trump Supporter Screen Names.txt',
    sanders_handle: 'Sanders Supporter Screen Names.txt',
    cruz_handle: 'Cruz Supporter Screen Names.txt',
    clinton_handle: 'Clinton Supporter Screen Names.txt',
}

candidate_supporter_tweets_folders = {
    trump_handle: TRUMP_SUPPORTER_TWEETS_FOLDER,
    sanders_handle: SANDERS_SUPPORTER_TWEETS_FOLDER,
    cruz_handle: CRUZ_SUPPORTER_TWEETS_FOLDER,
    clinton_handle: CLINTON_SUPPORTER_TWEETS_FOLDER,
}

def import_clear_supporters():
    for candidate_handle in candidate_handles:
        # scrape tweets also puts supporter metadata into csv file first line
        scrape_tweets(api, candidate_handle, candidate_supporter_tweets_folders[candidate_handle], candidate_supporters[candidate_handle])

def import_retweeters_from_tweet(tweet_id, supporter_handle):
    for retweet in api.retweets(tweet_id):
        print retweet.author.screen_name


import_clear_supporters()
# print match_by_handle(api, 'Parker9_', 10)
import_retweeters_from_tweet(713755536236228608, clinton_handle)
