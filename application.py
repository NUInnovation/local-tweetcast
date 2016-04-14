from get_access_token import get_access_token
import tweepy
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash
import os

app = Flask(__name__)
app.config.from_object('config')

TRUMP_SUPPORTER_TWEETS_FOLDER = 'Trump Supporter Tweets'

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

clear_trump_follower_screen_names = [
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

clear_sanders_follower_screen_names = [
    'CopinHagen',
]


# this is for messing with the API
# trumpfollowers = api.followers(trump_handle)

# user = api.get_user(user_id=720528592094887936)

# print user.screen_name
# print user.profile_image_url
# print user.description
# print api.user_timeline(include_rts=False)[0].text

for trump_follower_screen_name in clear_trump_follower_screen_names:
    tweetfilepath = TRUMP_SUPPORTER_TWEETS_FOLDER + '/' + trump_follower_screen_name + '.txt'
    if not os.path.isfile(tweetfilepath):
        with open(tweetfilepath, 'w') as newtweetsfile:
            for tweet in api.user_timeline(screen_name = trump_follower_screen_name, include_rts=False):
                print tweet.text
                newtweetsfile.write(tweet.text.encode("UTF-8") + '\n')
