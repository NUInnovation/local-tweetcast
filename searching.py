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

# logging for gensim
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

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
    text = [word for word in clean_block_of_tweets.lower().split()]
    id_to_path_dict[len(corpus)] = path_to_tweets_csv
    dictionary.add_documents([text])
    corpus.append(dictionary.doc2bow(text))
    return dictionary, corpus, id_to_path_dict
# texts = [[word for word in document.lower().split() if word not in stoplist] for document in documents]
corpus = []
id_to_path_dict = {}
# frequency = defaultdict(int)
dictionary = corpora.Dictionary()
dictionary, corpus, id_to_path_dict = add_to_gensim_dictionary_and_corpus(dictionary, corpus, id_to_path_dict, 'Trump Supporter Tweets/asamjulian.csv')
dictionary, corpus, id_to_path_dict = add_to_gensim_dictionary_and_corpus(dictionary, corpus, id_to_path_dict, 'Trump Supporter Tweets/DarkStream.csv')
dictionary, corpus, id_to_path_dict = add_to_gensim_dictionary_and_corpus(dictionary, corpus, id_to_path_dict, 'Trump Supporter Tweets/jesskazen.csv')

tfidf = models.TfidfModel(corpus)

tfidf_corpus = tfidf[corpus]

index = similarities.MatrixSimilarity(tfidf[corpus], num_features=len(dictionary))

block_of_tweets = ''
with open('Trump Supporter Tweets/asamjulian.csv') as tweetsfile:
    tweetreader = csv.reader(tweetsfile)
    metadata = tweetreader.next()
    for tweetrow in tweetreader:
        tweetstring = tweetrow[0]
        block_of_tweets += tweetstring
clean_block_of_tweets = utils.any2unicode(block_of_tweets.replace('\n', ' ').replace('\t', ' '), errors='ignore')
text = [word for word in clean_block_of_tweets.lower().split()]

doc_to_check = text
vec_bow = dictionary.doc2bow(doc_to_check)
vec_tfidf = tfidf[vec_bow] # convert the query to TDIDF space
print [(id_to_path_dict[tup[0]], tup[1]) for tup in list(enumerate(index[vec_tfidf]))]

# sims = index[tfidf_corpus]

# pprint(list(enumerate(sims)))
