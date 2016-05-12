import os
import json
import csv
import uuid
import copy
from collections import Counter
import logging
from gensim import utils, corpora, models, similarities
from collections import defaultdict
from pprint import pprint
from api import candidate_supporter_tweets_folders, candidate_handles, candidate_supporters, trump_handle, clinton_handle, cruz_handle, sanders_handle
from random import shuffle
from sklearn import svm
import pickle
import twitter as tw
import tweepy
from config import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET
# logging for gensim
# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

stoplist = [line.rstrip('\n') for line in open('stoplist.txt')]

def add_to_gensim_dictionary_and_corpus(dictionary, corpus, id_to_path_dict, path_to_tweets_csv):
    # corpus should be a list (of lists), and dictionary must be a gensim dictionary
    block_of_tweets = ''
    with open(path_to_tweets_csv) as tweetsfile:
        tweetreader = csv.reader(tweetsfile)
        try:
            metadata = tweetreader.next()
        # this may fall through if the CSV is empty for some reason
        except:
            return dictionary, corpus, id_to_path_dict
        for tweetrow in tweetreader:
            tweetstring = tweetrow[0]
            block_of_tweets += tweetstring
    clean_block_of_tweets = utils.any2unicode(block_of_tweets.replace('\n', ' ').replace('\t', ' '), errors='ignore')
    text = [word for word in clean_block_of_tweets.lower().split() if word not in stoplist]
    id_to_path_dict[len(corpus)] = path_to_tweets_csv
    dictionary.add_documents([text])
    corpus.append(dictionary.doc2bow(text))
    return dictionary, corpus, id_to_path_dict

def split_to_testing_and_training(training_set_size_fraction):
    '''Returns a training and testing set along with a corpus and dictionary and id to path dictionary'''
    training_set = []
    testing_set = []

    for candidate_handle in candidate_handles:
        candidate_folder = candidate_supporter_tweets_folders[candidate_handle]
        dirlist = os.listdir(candidate_folder)
        dirlist = [file for file in dirlist if file.endswith('.csv')]
        shuffle(dirlist)
        for i in range(len(dirlist)):
            filepath = os.path.join(candidate_folder, dirlist[i])
            if i <= len(dirlist) * training_set_size_fraction:
                training_set.append(filepath)
            else:
                testing_set.append(filepath)

    return testing_set, training_set

def create_tfidf(training_set):
    # finished splitting into testing and training
    corpus = []
    id_to_path_dict = {}
    dictionary = corpora.Dictionary()

    for training_filepath in training_set:
        print 'adding', training_filepath, 'to corpus/dictionary...'
        dictionary, corpus, id_to_path_dict = add_to_gensim_dictionary_and_corpus(dictionary, corpus, id_to_path_dict, training_filepath)

    tfidf = models.TfidfModel(corpus)
    index = similarities.MatrixSimilarity(tfidf[corpus], num_features=len(dictionary))

    return tfidf, index, dictionary, id_to_path_dict, corpus

def classify_tfidf_knn(tfidf_model, dictionary, index, document_to_query, k_neighbors, id_to_path_dict, k_threshold):
    '''This returns None if of the top k_neighbors, the mode has less than k_threshold entries'''
    vec_bow = dictionary.doc2bow(document_to_query)
    vec_tfidf = tfidf_model[vec_bow] # convert the query to TDIDF space
    sortedresult = sorted([(id_to_path_dict[tup[0]], tup[1]) for tup in list(enumerate(index[vec_tfidf]))], key=lambda x: x[1], reverse=True)
    # print sortedresult
    topkdict = {}
    for i in range(k_neighbors):
        candidate = sortedresult[i][0].split('/')[0]
        if candidate not in topkdict:
            topkdict[candidate] = 1
        else:
            topkdict[candidate] += 1
    for folder, count in topkdict.iteritems():
        if count >= k_threshold:
            for candidate_handle, folder_name in candidate_supporter_tweets_folders.iteritems():
                if folder_name == folder:
                    return candidate_handle
    # mode = max(set([tup[0].split('/')[0] for tup in sortedresult[:k_neighbors]]), key=[tup[0].split('/')[0] for tup in sortedresult[:k_neighbors]].count)
    return None

def get_block_of_tweets(filepath):
    block_of_tweets = ''
    with open(filepath) as tweetsfile:
        tweetreader = csv.reader(tweetsfile)
        metadata = tweetreader.next()
        for tweetrow in tweetreader:
            tweetstring = tweetrow[0]
            block_of_tweets += tweetstring
    clean_block_of_tweets = utils.any2unicode(block_of_tweets.replace('\n', ' ').replace('\t', ' '), errors='ignore')
    text = [word for word in clean_block_of_tweets.lower().split() if word not in stoplist]
    return text

def test_tfidf_knn(training_set_size_fraction, k_neighbors, k_threshold):
    testing_set, training_set = split_to_testing_and_training(training_set_size_fraction)
    tfidf, index, dictionary, id_to_path_dict, corpus = create_tfidf(training_set)
    # now do the testing
    rightcount = 0
    wrongcount = 0
    nonecount = 0

    for testing_filepath in testing_set:
        try:
            text = get_block_of_tweets(testing_filepath)
            classification = classify_tfidf_knn(tfidf, dictionary, index, text, k_neighbors, id_to_path_dict, k_threshold)
            # print 'klass', classification
            if classification is not None:
                for candidate_handle, folder_name in candidate_supporter_tweets_folders.iteritems():
                    if folder_name == testing_filepath.split('/')[0]:
                        true_candidate = candidate_handle
                if classification == true_candidate:
                    rightcount += 1
                else:
                    wrongcount += 1
            else:
                nonecount += 1
        except:
            # still getting empty csv errors
            pass
    return rightcount / float(rightcount + wrongcount), nonecount / float(len(testing_set)),

def create_svm(training_set, dictionary):
    simple_training_vecs = [[0 for i in range(max(sorted(list(dictionary.iterkeys()))))] for trainer in training_set]
    for i in range(len(training_set)):
        # print dictionary.doc2bow(get_block_of_tweets(training_set[i]))
        for word_id_count_tup in dictionary.doc2bow(get_block_of_tweets(training_set[i])):
            # print i, word_id_count_tup[0]
            simple_training_vecs[i][word_id_count_tup[0] - 1] = word_id_count_tup[1]
    inv_candidate_supporter_tweets_folders = {v: k for k, v in candidate_supporter_tweets_folders.items()}
    training_classifications = [inv_candidate_supporter_tweets_folders[trainer.split('/')[0]] for trainer in training_set]
    clf = svm.SVC(kernel='rbf')
    clf.fit(simple_training_vecs, training_classifications)
    return clf

def test_tfidf_svm(training_set_size_fraction):
    testing_set, training_set = split_to_testing_and_training(training_set_size_fraction)
    tfidf, index, dictionary, id_to_path_dict, corpus = create_tfidf(training_set)
    # print dictionary.doc2bow(get_block_of_tweets(testing_set[0]))
    clf = create_svm(training_set, dictionary)
    inv_candidate_supporter_tweets_folders = {v: k for k, v in candidate_supporter_tweets_folders.items()}
    simple_testing_vecs = [[0 for i in range(max(sorted(list(dictionary.iterkeys()))))] for tester in testing_set]
    testing_classifications = [inv_candidate_supporter_tweets_folders[tester.split('/')[0]] for tester in testing_set]
    for i in range(len(testing_set)):
        for word_id_count_tup in dictionary.doc2bow(get_block_of_tweets(testing_set[i])):
            simple_testing_vecs[i][word_id_count_tup[0] - 1] = word_id_count_tup[1]

    rightcount = 0
    wrongcount = 0

    for i in range(len(testing_classifications)):
        if clf.predict(simple_testing_vecs[i]) == testing_classifications[i]:
            rightcount += 1
        else:
            wrongcount += 1
    return rightcount / float(rightcount + wrongcount)

def predict_candidate(blob_of_tweets, k_neighbors, k_threshold):
    training_set = []
    for candidate_handle in candidate_handles:
        candidate_folder = candidate_supporter_tweets_folders[candidate_handle]
        dirlist = os.listdir(candidate_folder)
        dirlist = [file for file in dirlist if file.endswith('.csv')]
        shuffle(dirlist)
        for i in range(len(dirlist)):
            filepath = os.path.join(candidate_folder, dirlist[i])
            training_set.append(filepath)

    tfidf, index, dictionary, id_to_path_dict, corpus = create_tfidf_from_file()

    clean_block_of_tweets = utils.any2unicode(blob_of_tweets.replace('\n', ' ').replace('\t', ' '), errors='ignore')
    text = [word for word in clean_block_of_tweets.lower().split() if word not in stoplist]

    return classify_tfidf_knn(tfidf, dictionary, index, text, k_neighbors, id_to_path_dict, k_threshold)

def get_candidate_percentages(sortedresult):
    x = { "CR": [0,0], "TR": [0,0], "CL": [0,0], "SA": [0,0]}
    res = { "CR": 0, "TR": 0, "CL": 0, "SA": 0}
    res_dem = { "Clinton": 0, "Sanders": 0}
    res_rep = { "Cruz": 0 , "Trump": 0}
    res_party = { "Democrat": 0, "Republican": 0 }
    for i in sortedresult:
        if i[0].startswith('Cruz'):
            x["CR"][0] += 1
            x["CR"][1] += i[1]
        elif i[0].startswith('Trump'):
            x["TR"][0] += 1
            x["TR"][1] += i[1]
        elif i[0].startswith('Sanders'):
            x["SA"][0] += 1
            x["SA"][1] += i[1]
        elif i[0].startswith('Clinton'):
            x["CL"][0] += 1
            x["CL"][1] += i[1]

    res["SA"] = x["SA"][1] / x["SA"][0]
    res["CL"] = x["CL"][1] / x["CL"][0]
    res["TR"] = x["TR"][1] / x["TR"][0]
    res["CR"] = x["CR"][1] / x["CR"][0]
    total = res["SA"] + res["CL"] + res["TR"] + res["CR"]
    res_party["Democrat"] = (res["SA"] + res["CL"]) / total
    res_party["Republican"] = (res["TR"] + res["CR"]) / total
    res_dem["Clinton"] = res["CL"] / (res["CL"] + res["SA"])
    res_dem["Sanders"] = res["SA"] / (res["CL"] + res["SA"])
    res_rep["Trump"] = res["TR"] / (res["TR"] + res["CR"])
    res_rep["Cruz"] = res["CR"] / (res["TR"] + res["CR"])

    winners = {}
    winners["party"] = max(res_party, key=res_party.get)
    winners["dem"] = max(res_dem, key=res_dem.get)
    winners["rep"] = max(res_rep, key=res_rep.get)


    return {"res_party": res_party, "res_dem":res_dem, "res_rep":res_rep, "winners":winners}

# def get_area_percentages(list_of_tweet_blobs, k_neighbors, k_threshold):
#     counts = {cruz_handle: 0, trump_handle: 0, clinton_handle: 0, sanders_handle: 0}
#     res_dem = { "Clinton": 0, "Sanders": 0}
#     res_rep = { "Cruz": 0 , "Trump": 0}
#     res_party = { "Democrat": 0, "Republican": 0 }
#     nonecount = 0
#     for blob in list_of_tweet_blobs:
#         candidate = predict_candidate(blob, k_neighbors, k_threshold)
#         if candidate is not None:
#             counts[candidate] += 1
#         else:
#             nonecount += 1
#
#     total = float(sum([count for candidate, count in counts.iteritems()]))
#     res_party["Democrat"] = (counts[sanders_handle] + counts[clinton_handle]) / total
#     res_party["Republican"] = (counts[trump_handle] + counts[clinton_handle]) / total
#     res_dem["Clinton"] = counts[clinton_handle] / (counts[clinton_handle] + counts[sanders_handle])
#     res_dem["Sanders"] = counts[sanders_handle] / (counts[clinton_handle] + counts[sanders_handle])
#     res_rep["Trump"] = counts[trump_handle] / (counts[trump_handle] + counts[cruz_handle])
#     res_rep["Cruz"] = counts[cruz_handle] / (counts[trump_handle] + counts[cruz_handle])
#
#     winners = {}
#     winners["party"] = max(res_party, key=res_party.get)
#     winners["dem"] = max(res_dem, key=res_dem.get)
#     winners["rep"] = max(res_rep, key=res_rep.get)
#
#     print 'NONECOUNT', nonecount
#     return {"res_party": res_party, "res_dem":res_dem, "res_rep":res_rep, "winners":winners}

def save_dictionary_and_corpus_to_file():
    testing_set, training_set = split_to_testing_and_training(1.0)
    tfidf, index, dictionary, id_to_path_dict, corpus = create_tfidf(training_set)
    dictionary.save('gensim_dictionary.dict')
    corpora.MmCorpus.serialize('gensim_corpus.mm', corpus)
    pickle.dump( id_to_path_dict, open( "id_to_path_dict.p", "wb" ) )

def create_tfidf_from_file():
    corpus = corpora.MmCorpus('gensim_corpus.mm')
    dictionary = corpora.Dictionary.load('gensim_dictionary.dict')
    id_to_path_dict = pickle.load( open( "id_to_path_dict.p", "rb" ) )
    tfidf = models.TfidfModel(corpus)
    index = similarities.MatrixSimilarity(tfidf[corpus], num_features=len(dictionary))

    return tfidf, index, dictionary, id_to_path_dict, corpus

def get_area_percentages(location, k_neighbors, k_threshold):
    tweets = tw.get_tweets_from_location(api, location)
    print len(tweets)
    if tweets:
        users = tw.get_users_from_tweets(api, tweets)
        print 'numusers', len(users)
        if users:
            corpus = tw.get_tweets_from_users(api, users)
            for i in range(len(corpus)):
                print predict_candidate(corpus[i], k_neighbors, k_threshold)
                print users[i]
            # guess, res = srch.predict_candidate(corpus, 10)
# save_dictionary_and_corpus_to_file()
get_area_percentages('Evanston, IL', 10, 7)
# tweets = tw.get_tweets_from_location(api, location)

# create_tfidf_from_file()
# testdict = {}
# # for i in range(3, 30):
# testdict[7] = test_tfidf(0.3, 7)
# testdict = {}
# # for i in range(3, 30):
# testdict[7] = test_tfidf_knn(0.7, 10, )
# pprint(test_tfidf_svm(0.7))
# testing_dict = {}
# for kn in range(4, 18):
#     testing_dict[kn] = test_tfidf(0.7, kn)
# pprint(testdict)
