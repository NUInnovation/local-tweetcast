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

# logging for gensim
# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

stoplist = [line.rstrip('\n') for line in open('stoplist.txt')]

def add_to_gensim_dictionary_and_corpus(dictionary, corpus, id_to_path_dict, path_to_tweets_csv):
    # corpus should be a list (of lists), and dictionary must be a gensim dictionary
    block_of_tweets = ''
    with open(path_to_tweets_csv) as tweetsfile:
        tweetreader = csv.reader(tweetsfile)
        metadata = tweetreader.next()
        for tweetrow in tweetreader:
            tweetstring = tweetrow[0]
            block_of_tweets += tweetstring
    clean_block_of_tweets = utils.any2unicode(block_of_tweets.replace('\n', ' ').replace('\t', ' '), errors='ignore')
    text = [word for word in clean_block_of_tweets.lower().split() if word not in stoplist]
    id_to_path_dict[len(corpus)] = path_to_tweets_csv
    dictionary.add_documents([text])
    corpus.append(dictionary.doc2bow(text))
    return dictionary, corpus, id_to_path_dict

def add_to_gensim_hashtag_dictionary_and_corpus(hashtag_dict, hashtag_corpus, id_to_path_dict_hashtag, path_to_tweets_csv):
    block_of_tweets = ''
    with open(path_to_tweets_csv) as tweetsfile:
        tweetreader = csv.reader(tweetsfile)
        metadata = tweetreader.next()
        for tweetrow in tweetreader:
            tweetstring = tweetrow[0]
            block_of_tweets += tweetstring
    clean_block_of_tweets = utils.any2unicode(block_of_tweets.replace('\n', ' ').replace('\t', ' '), errors='ignore')
    text = [word for word in clean_block_of_tweets.lower().split() if word not in stoplist and word[0] == '#']
    id_to_path_dict_hashtag[len(hashtag_corpus)] = path_to_tweets_csv
    hashtag_dict.add_documents([text])
    hashtag_corpus.append(hashtag_dict.doc2bow(text))
    return hashtag_dict, hashtag_corpus, id_to_path_dict_hashtag

def test_tfidf(training_set_size_fraction, k_neighbors):
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

    corpus = []
    id_to_path_dict = {}
    dictionary = corpora.Dictionary()

    hashtag_corpus = []
    id_to_path_dict_hashtag = {}
    hashtag_dictionary = corpora.Dictionary()

    for training_filepath in training_set:
        print 'adding', training_filepath, 'to corpus/dictionary...'
        dictionary, corpus, id_to_path_dict = add_to_gensim_dictionary_and_corpus(dictionary, corpus, id_to_path_dict, training_filepath)
        hashtag_dictionary, hashtag_corpus, id_to_path_dict_hashtag = add_to_gensim_hashtag_dictionary_and_corpus(hashtag_dictionary, hashtag_corpus, id_to_path_dict_hashtag, training_filepath)

    tfidf = models.TfidfModel(corpus)
    tfidf_corpus = tfidf[corpus]
    index = similarities.MatrixSimilarity(tfidf[corpus], num_features=len(dictionary))

    tfidf_hashtag = models.TfidfModel(hashtag_corpus)
    tfidf_corpus_hashtag = tfidf_hashtag[hashtag_corpus]
    index_hashtag = similarities.MatrixSimilarity(tfidf_hashtag[hashtag_corpus], num_features=len(hashtag_dictionary))

    rightcount = 0
    wrongcount = 0

    rightcount_hashtag = 0
    wrongcount_hashtag = 0

    for testing_filepath in testing_set:
        block_of_tweets = ''
        with open(testing_filepath) as tweetsfile:
            print 'adding', testing_filepath, 'to testing set...'
            tweetreader = csv.reader(tweetsfile)
            metadata = tweetreader.next()
            for tweetrow in tweetreader:
                tweetstring = tweetrow[0]
                block_of_tweets += tweetstring
        clean_block_of_tweets = utils.any2unicode(block_of_tweets.replace('\n', ' ').replace('\t', ' '), errors='ignore')
        text = [word for word in clean_block_of_tweets.lower().split() if word not in stoplist]
        hashtag_text = [word for word in clean_block_of_tweets.lower().split() if word not in stoplist and word[0] == '#']

        doc_to_check = text
        vec_bow = dictionary.doc2bow(doc_to_check)
        vec_tfidf = tfidf[vec_bow] # convert the query to TDIDF space
        sortedresult = sorted([(id_to_path_dict[tup[0]], tup[1]) for tup in list(enumerate(index[vec_tfidf]))], key=lambda x: x[1], reverse=True)
        mode = max(set([tup[0].split('/')[0] for tup in sortedresult[:k_neighbors]]), key=[tup[0].split('/')[0] for tup in sortedresult[:k_neighbors]].count)
        if mode == testing_filepath.split('/')[0]:
            rightcount += 1
        else:
            wrongcount += 1

        doc_to_check_hashtag = hashtag_text
        vec_bow_hashtag = hashtag_dictionary.doc2bow(doc_to_check_hashtag)
        vec_tfidf_hashtag = tfidf_hashtag[vec_bow_hashtag] # convert the query to TDIDF space
        sortedresult_hashtag = sorted([(id_to_path_dict[tup[0]], tup[1]) for tup in list(enumerate(index_hashtag[vec_tfidf_hashtag]))], key=lambda x: x[1], reverse=True)
        mode_hashtag = max(set([tup[0].split('/')[0] for tup in sortedresult_hashtag[:k_neighbors]]), key=[tup[0].split('/')[0] for tup in sortedresult[:k_neighbors]].count)
        if mode_hashtag == testing_filepath.split('/')[0]:
            rightcount_hashtag += 1
        else:
            wrongcount_hashtag += 1
    return rightcount / float(rightcount + wrongcount), rightcount_hashtag / float(rightcount_hashtag + wrongcount_hashtag)

def predict_candidate(blob_of_tweets, k_neighbors):
    corpus = []
    id_to_path_dict = {}
    dictionary = corpora.Dictionary()

    for candidate_handle in candidate_handles:
        candidate_folder = candidate_supporter_tweets_folders[candidate_handle]
        dirlist = os.listdir(candidate_folder)
        dirlist = [file for file in dirlist if file.endswith('.csv')]
        shuffle(dirlist)
        for i in range(len(dirlist)):
            filepath = os.path.join(candidate_folder, dirlist[i])
            print 'adding', training_filepath, 'to corpus/dictionary...'
            dictionary, corpus, id_to_path_dict = add_to_gensim_dictionary_and_corpus(dictionary, corpus, id_to_path_dict, training_filepath)

    clean_block_of_tweets = utils.any2unicode(blob_of_tweets.replace('\n', ' ').replace('\t', ' '), errors='ignore')
    text = [word for word in clean_block_of_tweets.lower().split() if word not in stoplist]

    doc_to_check = text
    vec_bow = dictionary.doc2bow(doc_to_check)
    vec_tfidf = tfidf[vec_bow] # convert the query to TDIDF space
    sortedresult = sorted([(id_to_path_dict[tup[0]], tup[1]) for tup in list(enumerate(index[vec_tfidf]))], key=lambda x: x[1], reverse=True)
    mode = max(set([tup[0].split('/')[0] for tup in sortedresult[:k_neighbors]]), key=[tup[0].split('/')[0] for tup in sortedresult[:k_neighbors]].count)
    for candidate_handle, folder_name in candidate_supporter_tweets_folders.iteritems():
        if folder_name == mode:
            return candidate_handle

print test_tfidf(0.7, 10)
