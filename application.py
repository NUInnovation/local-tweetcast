from get_access_token import get_access_token
import tweepy
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

app = Flask(__name__)
app.config.from_object('config')

auth = tweepy.OAuthHandler(app.config['CONSUMER_KEY'], app.config['CONSUMER_SECRET'])
auth.set_access_token(app.config['ACCESS_TOKEN_KEY'], app.config['ACCESS_TOKEN_SECRET'])

api = tweepy.API(auth)

public_tweets = api.home_timeline()
for tweet in public_tweets:
    print tweet.text
