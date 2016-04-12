from get_access_token import get_access_token
import twitter
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

app = Flask(__name__)
app.config.from_object('config')

api = twitter.Api(consumer_key=app.config['CONSUMER_KEY'],
                      consumer_secret=app.config['CONSUMER_SECRET'],
                      access_token_key=app.config['ACCESS_TOKEN_KEY'],
                      access_token_secret=app.config['ACCESS_TOKEN_SECRET'])

print api.VerifyCredentials()
