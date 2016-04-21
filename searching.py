import os
import json
# import pprint
import csv
import uuid
from pyelasticsearch import ElasticSearch, exceptions

# pp = pprint.PrettyPrinter(indent = 4)

es = ElasticSearch('http://localhost:9200/')

# def get_max_obvious_supporter_id():
#     query = {
#       'filter': {
#         'type' : {
#           'value' : 'obvioussupporter'
#         }
#       },
#       'sort': {
#         '_id': {
#           'order': 'desc'
#         }
#       },
#       'size': 1
#     }
#     try:
#         max_id = es.search(query, index='localtweetcast')['hits']['hits'][0]['_id']
#     except exceptions.ElasticHttpNotFoundError as err:
#         if err[1] == 'index_not_found_exception':
#             # we haven't added anything yet
#             max_id = 0
#         else:
#             raise Exception('Unexpected ElasticSearch Error')
#     return int(max_id)

def import_obvious_supporter(supporter_name, supporter_handle, supporter_location, id, candidate_handle, supporter_tweets):
    es.index('localtweetcast',
             'obvioussupporter',
             {'supporter_name': supporter_name, 'supporter_handle': supporter_handle, 'supporter_location': supporter_location, 'candidate_handle': candidate_handle, 'supporter_tweets': supporter_tweets}, id=id)

def get_obvious_supporter(supporter_handle):
    return es.search('supporter_handle:' + supporter_handle, index='localtweetcast')

def get_number_of_obvious_supporters():
    emptyquery = {
    'filter': {
        'type': {
            'value': 'obvioussupporter'
            }
        }
    }
    return int(es.count(emptyquery, index='localtweetcast', doc_type='obvioussupporter')['count'])

def add_tweets_to_elastic(directory, candidate_handle):
    list_dir = os.listdir(directory)
    # init_max_id = get_max_obvious_supporter_id()
    # cur_id = init_max_id
    for file in list_dir:
        if file.endswith('.csv'):
            data_to_copy = []
            metadata_to_change = {}
            with open(os.path.join(directory, file), 'r') as readfile:
                data = csv.reader(readfile)
                metadata_json_row = data.next()
                metadata = json.loads(metadata_json_row[0])
                metadata_to_change = metadata
                if metadata['imported_to_elastic'] == False:

                    tweets = []
                    for tweetrow in data:
                        tweets.append(tweetrow[0])
                        data_to_copy.append(tweetrow)
                    tweets_as_one_string = ''.join(tweets)
                    supporter_name = metadata['name']
                    supporter_handle = os.path.splitext(file)[0]
                    supporter_location = metadata['location']
                    new_id = str(uuid.uuid4())
                    import_obvious_supporter(supporter_name, supporter_handle, supporter_location, new_id, candidate_handle, tweets_as_one_string)
                    metadata_to_change['imported_to_elastic'] = True
                    with open(os.path.join(directory, file), 'w') as newfile:
                        newwriter = csv.writer(newfile)
                        newwriter.writerow([json.dumps(metadata_to_change)])
                        newwriter.writerows(data_to_copy)
                    print 'imported user with handle', supporter_handle, 'and id', new_id


# print es.get('localtweetcast', 'obvioussupporter', 15)
