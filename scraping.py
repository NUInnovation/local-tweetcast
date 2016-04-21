import os
import tweepy
import csv

def scrape_tweets(app, api, candidate_handle, candidate_supporter_tweets_folder, candidate_supporter_screen_names):
    for candidate_supporter_screen_name in candidate_supporter_screen_names:
        tweetsfilepath = candidate_supporter_tweets_folder + '/' + candidate_supporter_screen_name + '.csv'
        if not os.path.isfile(tweetsfilepath):
            with open(tweetsfilepath, 'w') as newtweetsfile:
                csvwriter = csv.writer(newtweetsfile)
                for tweet in api.user_timeline(screen_name = candidate_supporter_screen_name, include_rts=False, count = 200):
                    print tweet.text
                    # for string in tweet.text:
                    #     stringentry = db.candidate_handle.find({'string': string})
                    #     if stringentry:
                    #         stringentry['count'] += 1
                    #     else:
                    #         db[candidate_handle].insert({'string': string, 'count': 1})
                    csvwriter.writerow([tweet.text.encode("UTF-8")])
