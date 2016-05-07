import tweepy
import random
from sets import Set
from geopy.geocoders import Nominatim
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash

def get_tweets_from_location(api, loc):
    geolocator = Nominatim()
    loc_geo = geolocator.geocode(loc)
    if loc_geo is not None:
        return get_tweets_from_geo(api, loc_geo)
    else:
        return None


def get_tweets_from_geo(api, loc_geo):
    q = ""
    geocode = "{0},{1},{2}".format(loc_geo.latitude,loc_geo.longitude,"5mi")
    a = api.search(q=q,geocode=geocode)
    return a

def get_users_from_tweets(api, tweets):
    loc_users = Set()
    for tweet in tweets:
        try:
            loc_users.add(tweet.user.screen_name)
        except:
            pass
    return loc_users

def get_tweets_from_users(api, users):
    txt = ""
    usr_count = min(10, len(users))
    usrs = random.sample(users, usr_count)
    for user in usrs:
        user_tweets = api.user_timeline(id=user)
        for tweet in user_tweets:
            try:
                txt += str(tweet.text)
            except:
                pass
    return txt
