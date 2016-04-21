import os
import json
# import pprint
from pyelasticsearch import ElasticSearch, exceptions

# pp = pprint.PrettyPrinter(indent = 4)

es = ElasticSearch('http://localhost:9200/')

def get_max_obvious_supporter_id():
    query = {
      'filter': {
        'type' : {
          'value' : 'obvioussupporter'
        }
      },
      'sort': {
        '_id': {
          'order': 'desc'
        }
      },
      'size': 1
    }
    try:
        max_id = es.search(query, index='localtweetcast')['hits']['hits'][0]['_id']
    except exceptions.ElasticHttpNotFoundError as err:
        if err[1] == 'index_not_found_exception':
            # we haven't added anything yet
            max_id = 0
        else:
            raise Exception('Unexpected ElasticSearch Error')
    return max_id

def import_obvious_supporter(supporter_name, supporter_handle, supporter_location, id, candidate_handle, supporter_tweets):
    es.index('localtweetcast',
             'obvioussupporter',
             {'supporter_name': supporter_name, 'supporter_handle': supporter_handle, 'supporter_location': supporter_location, 'candidate_handle': candidate_handle, 'supporter_tweets': supporter_tweets}, id=id)

def get_obvious_supporter(supporter_handle):
    return es.search('supporter_handle:' + supporter_handle, index='localtweetcast')
