import tweepy
import os
from scraping import scrape_tweets
import csv
import copy
import json
import uuid
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

clear_trump_supporter_screen_names = [
    'michaelpshipley',
    'wyomobe',
    'jesskazen',
    'JosephineMigli2',
    'shadohchaser',
    'Tarmas55',
    'scalpatriot',
    'asamjulian',
    'DarkStream',
]

clear_sanders_supporter_screen_names = [
    'CopinHagen',
    'MediaPhiled',
    'french_monica',
    'LilyStarlette',
    'Marnie_was_here',
    'Thinkers4Bernie',
    'AudreyGoz',
    'MinervaAventine',
    'sharon211',
    'joavargas_1220',
    'dsptchsfrmexile',
    'TheTardisDoc',
    'angelam314'
]

clear_cruz_supporter_screen_names = [

]

clear_clinton_supporter_screen_names = [

]

candidate_supporters = {
    trump_handle: clear_trump_supporter_screen_names,
    sanders_handle: clear_sanders_supporter_screen_names,
    cruz_handle: clear_cruz_supporter_screen_names,
    clinton_handle: clear_clinton_supporter_screen_names,
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

import_clear_supporters()
# print match_by_handle(api, 'Parker9_', 10)
