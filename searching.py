import os
import json
# import pprint
from pyelasticsearch import ElasticSearch

# pp = pprint.PrettyPrinter(indent = 4)

es = ElasticSearch('http://localhost:9200/')

# first get max ID
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

max_id = es.search(query, index='localtweetcast')['hits']['hits'][0]['_id']

list_dir = os.listdir('Trump Supporter Tweets')
print list_dir
# for file in list_dir:
#     if file.endswith('.csv'):


es.index('localtweetcast',
'obvioussupporter',
{'name': 'Sam Tester', 'handle': 'sam_test_handle', 'location': 'Samvill, IL', 'candidate':'Trump'}, id=2)

# print es.search('name:joe OR name:freddy', index='localtweetcast')
