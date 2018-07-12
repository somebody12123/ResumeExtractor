#!/usr/bin/python 
# -*- coding: utf-8 -*-

import pymongo

def insert_many(database_name:str,conllection_name,docs:list):

    client=pymongo.MongoClient('127.0.0.1',27017)
    db=client.get_database(database_name)
    collection=db.get_collection(conllection_name)
    # db=client.extractor
    # collection=db.regular
    collection.insert_many(docs)
    client.close()
    print('insert right')


def insert_one(database_name:str,conllection_name,doc:dict):

    client=pymongo.MongoClient('127.0.0.1',27017)
    # db = client.extractor
    # collection = db.regular
    db = client.get_database (database_name)
    collection = db.get_collection (conllection_name)
    collection.insert(doc)
    client.close()
    print ('insert right')