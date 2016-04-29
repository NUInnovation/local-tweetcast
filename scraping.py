import os
import tweepy
import csv
import json

def scrape_tweets(api, candidate_handle, candidate_supporter_tweets_folder, candidate_supporter_screen_names):
    for candidate_supporter_screen_name in candidate_supporter_screen_names:
        tweetsfilepath = candidate_supporter_tweets_folder + '/' + candidate_supporter_screen_name + '.csv'
        if not os.path.isfile(tweetsfilepath):
            with open(tweetsfilepath, 'w') as newtweetsfile:
                csvwriter = csv.writer(newtweetsfile)
                user_info = api.get_user(screen_name = candidate_supporter_screen_name)._json
                user_info['imported_to_gensim'] = False
                csvwriter.writerow([json.dumps(user_info).encode("UTF-8")])
                for tweet in api.user_timeline(screen_name = candidate_supporter_screen_name, include_rts=False, count = 200):
                    csvwriter.writerow([tweet.text.encode("UTF-8")])
