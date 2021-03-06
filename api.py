import tweepy
import os
from scraping import scrape_tweets
import csv
import copy
import json
import uuid
from pprint import pprint
from config import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_SECRET, ACCESS_TOKEN_KEY
import botornot

twitter_app_auth = {
    'consumer_key': CONSUMER_KEY,
    'consumer_secret': CONSUMER_SECRET,
    'access_token': ACCESS_TOKEN_KEY,
    'access_token_secret': ACCESS_TOKEN_SECRET,
  }
bon = botornot.BotOrNot(**twitter_app_auth)

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
    candidate_supporter_screen_names = [line.rstrip('\n') for line in open(candidate_supporters[supporter_handle])]
    for retweet in api.retweets(tweet_id, count=100):
        screen_name = retweet.author.screen_name
        print 'checking if', screen_name, 'is a bot...'
        if screen_name not in candidate_supporter_screen_names:
            score = bon.check_account('@' + screen_name)['score']
            if score < 0.40:
                print 'not a bot! -', score
                # this means its probably not a bot
                with open(candidate_supporters[supporter_handle], 'a') as file:
                    file.write(screen_name + '\n')
            else:
                print screen_name, 'is a bot! -', score

if __name__ == "__main__":
    import_clear_supporters()
    # print match_by_handle(api, 'Parker9_', 10)
    # import_retweeters_from_tweet(713755536236228608, clinton_handle)
    # import_retweeters_from_tweet(724945973353562113, clinton_handle)
    # import_retweeters_from_tweet(722408699290132480, clinton_handle)
    # import_retweeters_from_tweet(718157344656363520, sanders_handle)
    # import_retweeters_from_tweet(713050304707571712, sanders_handle)
    # import_retweeters_from_tweet(717338087387492352, clinton_handle)
    # import_retweeters_from_tweet(698197228578566144, trump_handle)
    # import_retweeters_from_tweet(697465953412468736, cruz_handle)
    # import_retweeters_from_tweet(715976510331600896, trump_handle)
    # import_retweeters_from_tweet(647915807436054528, trump_handle)
    # import_retweeters_from_tweet(694379667730649088, clinton_handle)
    # import_retweeters_from_tweet(663113220081618944, trump_handle)
    # import_retweeters_from_tweet(695448991337545728, sanders_handle)
    # import_retweeters_from_tweet(709186515964862464, trump_handle)
    # import_retweeters_from_tweet(696785353827602433, sanders_handle)

