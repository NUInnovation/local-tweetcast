from get_access_token import get_access_token
import tweepy
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash
import os
from scraping import scrape_tweets

app = Flask(__name__)
app.config.from_object('config')

TRUMP_SUPPORTER_TWEETS_FOLDER = 'Trump Supporter Tweets'
SANDERS_SUPPORTER_TWEETS_FOLDER = 'Sanders Supporter Tweets'
CRUZ_SUPPORTER_TWEETS_FOLDER = 'Cruz Supporter Tweets'
CLINTON_SUPPORTER_TWEETS_FOLDER = 'Clinton Supporter Tweets'


auth = tweepy.OAuthHandler(app.config['CONSUMER_KEY'], app.config['CONSUMER_SECRET'])
auth.set_access_token(app.config['ACCESS_TOKEN_KEY'], app.config['ACCESS_TOKEN_SECRET'])

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


# this is for messing with the API
# trumpfollowers = api.followers(trump_handle)

# user = api.get_user(user_id=720528592094887936)

# print user.screen_name
# print user.profile_image_url
# print user.description
# print api.user_timeline(include_rts=False)[0].text

for candidate_handle in candidate_handles:
    scrape_tweets(api, candidate_handle, candidate_supporter_tweets_folders[candidate_handle], candidate_supporters[candidate_handle])
