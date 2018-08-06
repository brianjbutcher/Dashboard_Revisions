from pymongo import MongoClient
import pymongo
import os
#import pandas as pd
import ast
import json

import logging
import time

_logger = logging.getLogger(__name__)


def printCSV(df, output_dir, filename):
    file = str(filename + '.csv')
    if os.path.isfile(os.path.join(output_dir, file)):
        print ("Appending..." + filename + '.csv')
        with open(os.path.join(output_dir, file), 'a') as f:
            df.to_csv(f, sep=",", index=False, header=False)
        print("\n\n")

    elif os.path.isfile(os.path.join(output_dir, file)) == False:
        print ("Creating..." + filename + '.csv')
        df.to_csv(os.path.join(output_dir, file), sep=",", index=False)

    return


mongo_server = '10.196.155.85:27017'

def __connect_mongo__(server=mongo_server, username=None, password=None):
    """ A util for making a connection to mongo """
    if username and password:
        mongo_uri = 'mongodb://%s:%s@%s' % (username, password, server)
    else:
        mongo_uri = 'mongodb://%s' % (server)
    return MongoClient(mongo_uri)

mongo_client = __connect_mongo__()

def get_databases(db = None):
    if db:
        return mongo_client[db]
    else:
        return tuple(mongo_client[each] for each in mongo_client.list_database_names())



def get_collection_map():
    '''PARAMS:
       RETURNS: 1) a dictionary of db names and collection names 2) unique product list
       FUNC:
    '''
    return dict(
        (db.name, tuple(db.collection_names())) 
        for db in get_databases()
        )


def run_query_unique(db, collection, query, unique):
    """ Read from Mongo and Store into DataFrame """
    # Connect to MongoDB
    db = get_databases(db = db)
    return db[collection].distinct(unique, query)
    #return tuple(cursor)



def run_query(db, collection, query, limit = 0):
    """ Read from Mongo and Store into DataFrame """
    # Connect to MongoDB
    db = get_databases(db = db)
    # print(db)
    # Make a query to the specific DB and Collection
    #cursor = db[collection].find( {'TEST_TYPE':'(Read)BES-(PD_ESS_XXXXXX)'},{'HISTO.SFR': True})
    cursor = db[collection].find(query).limit(limit)

    return tuple(cursor)


def get_ranking(db, collection, query, field, top = 1):
    """ Read from Mongo and Store into DataFrame """
    # Connect to MongoDB
    db = get_databases(db = db)
    # print(db)
    # Make a query to the specific DB and Collection
    #cursor = db[collection].find( {'TEST_TYPE':'(Read)BES-(PD_ESS_XXXXXX)'},{'HISTO.SFR': True})
    cursor = db[collection].find(query).sort(field, pymongo.DESCENDING).limit(top)
    #import pdb;pdb.set_trace()
    #, {'value': True}
    # cursor = db[collection].find({$and:[{'TEST_TYPE': '(Read)BES-(PD_ESS_XXXXXX)'},{'HISTO.SFR': True, 'HISTO.FBC(bin)': True}]})
    # cursor = db[collection].find(query)
    # from pprint import pprint
    # thispath = os.path.dirname(os.path.realpath(__file__))

    return tuple(cursor)


'''

#query = {'TEST_TYPE':'(Read)DRT-(PD_ESS_LO4p1_TMM5p5)'}
query={'TEST_TYPE': '(Read)BES-(PD_ESS_XXXXXX)'}
df = read_mongo('DEMO_2_20_18','DEMOCOLL', query)
print(df)



data = {"x":[], "y":[], "label":[]}
#for coord in df.HISTO.items():
#print(df.HISTO[0]['FBC(bin)'])
df.HISTO[0]['FBC(bin)'].pop(0)

print(data)

import random
import sys
import array
import matplotlib.pyplot as plt

# display scatter plot data
plt.figure(figsize=(10,8))
plt.title(query['TEST_TYPE'], fontsize=20)
plt.xlabel('x', fontsize=15)
plt.ylabel('y', fontsize=15)
plt.scatter(df.HISTO[0]['FBC(bin)'], df.HISTO[0]['FBC(cnt)'], marker = 'o')

# add labels
#for label, x, y in zip(data["label"], data["x"], data["y"]):
#    plt.annotate(label, xy = (x, y))

plt.savefig('foo.png')

thispath =os.path.dirname(os.path.realpath(__file__))
printCSV(df,thispath,'test')
'''