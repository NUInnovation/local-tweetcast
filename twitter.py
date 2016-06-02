import tweepy
import random
from sets import Set
from geopy.geocoders import Nominatim
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash

def get_tweets_from_location(api, loc):
    geolocator = Nominatim()
    print loc
    loc_geo = geolocator.geocode(loc)
    if loc_geo is not None:
        return get_tweets_from_geo(api, loc_geo)
    else:
        return None


def get_tweets_from_geo(api, loc_geo):
    q = ""
    geocode = "{0},{1},{2}".format(loc_geo.latitude,loc_geo.longitude,"5mi")
    a = api.search(q=q,geocode=geocode, count=100)
    return a

def get_users_from_tweets(api, tweets):
    loc_users = Set()
    for tweet in tweets:
        try:
            loc_users.add(tweet.user.screen_name)
        except:
            pass
    return list(loc_users)

def get_tweets_from_users(api, users):
    txts = []
    usr_count = min(20, len(users))
    usrs = random.sample(users, usr_count)
    ct = 0
    for user in usrs:
        print user
        ct += 1
        txt = ""
        user_tweets = api.user_timeline(id=user, count=200)
        for tweet in user_tweets:
            try:
                txt += str(tweet.text)
            except:
                pass
        txts.append(txt)
        print 'done', ct
    return txts
