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
from api import candidate_supporter_tweets_folders, candidate_handles, candidate_supporters
from random import shuffle
from sklearn import svm
# logging for gensim
# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

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

    return tfidf, index, dictionary, id_to_path_dict

def classify_tfidf_knn(tfidf_model, dictionary, index, document_to_query, k_neighbors, id_to_path_dict):
    vec_bow = dictionary.doc2bow(document_to_query)
    vec_tfidf = tfidf_model[vec_bow] # convert the query to TDIDF space
    sortedresult = sorted([(id_to_path_dict[tup[0]], tup[1]) for tup in list(enumerate(index[vec_tfidf]))], key=lambda x: x[1], reverse=True)
    mode = max(set([tup[0].split('/')[0] for tup in sortedresult[:k_neighbors]]), key=[tup[0].split('/')[0] for tup in sortedresult[:k_neighbors]].count)
    for candidate_handle, folder_name in candidate_supporter_tweets_folders.iteritems():
        if folder_name == mode:
            return candidate_handle

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

def test_tfidf_knn(training_set_size_fraction, k_neighbors):
    testing_set, training_set = split_to_testing_and_training(training_set_size_fraction)
    tfidf, index, dictionary, id_to_path_dict = create_tfidf(training_set)
    # now do the testing
    rightcount = 0
    wrongcount = 0

    for testing_filepath in testing_set:
        try:
            text = get_block_of_tweets(testing_filepath)
            classification = classify_tfidf_knn(tfidf, dictionary, index, text, k_neighbors, id_to_path_dict)
            for candidate_handle, folder_name in candidate_supporter_tweets_folders.iteritems():
                if folder_name == testing_filepath.split('/')[0]:
                    true_candidate = candidate_handle
            if classification == true_candidate:
                rightcount += 1
            else:
                wrongcount += 1
        except:
            # still getting empty csv errors
            pass
    return rightcount / float(rightcount + wrongcount)

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
    tfidf, index, dictionary, id_to_path_dict = create_tfidf(training_set)
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

def predict_candidate(blob_of_tweets, k_neighbors):
    training_set = []
    for candidate_handle in candidate_handles:
        candidate_folder = candidate_supporter_tweets_folders[candidate_handle]
        dirlist = os.listdir(candidate_folder)
        dirlist = [file for file in dirlist if file.endswith('.csv')]
        shuffle(dirlist)
        for i in range(len(dirlist)):
            filepath = os.path.join(candidate_folder, dirlist[i])
            training_set.append(filepath)

    tfidf, index, dictionary, id_to_path_dict = create_tfidf(training_set)

    clean_block_of_tweets = utils.any2unicode(blob_of_tweets.replace('\n', ' ').replace('\t', ' '), errors='ignore')
    text = [word for word in clean_block_of_tweets.lower().split() if word not in stoplist]

    return classify_tfidf_knn(tfidf, dictionary, index, text, k_neighbors, id_to_path_dict)


# testdict = {}
# # for i in range(3, 30):
# testdict[7] = test_tfidf(0.3, 7)
testdict = {}
# # for i in range(3, 30):
testdict[7] = test_tfidf_knn(0.7, 7)
# pprint(test_tfidf_svm(0.7))
# testing_dict = {}
# for kn in range(4, 18):
#     testing_dict[kn] = test_tfidf(0.7, kn)
pprint(testdict)
