import os
import tweepy
import csv

def scrape_tweets(api, candidate_handle, candidate_supporter_tweets_folder, candidate_supporter_screen_names):
    for candidate_supporter_screen_name in candidate_supporter_screen_names:
        tweetsfilepath = candidate_supporter_tweets_folder + '/' + candidate_supporter_screen_name + '.csv'
        if not os.path.isfile(tweetsfilepath):
            with open(tweetsfilepath, 'w') as newtweetsfile:
                csvwriter = csv.writer(newtweetsfile)
                for tweet in api.user_timeline(screen_name = candidate_supporter_screen_name, include_rts=False):
                    print tweet.text
                    csvwriter.writerow([tweet.text.encode("UTF-8")])
