from pymongo import MongoClient
import pymongo

def mongo_connect():

    try:
         # Provide the mongodb atlas url to connect python to mongodb using pymongo
        CONNECTION_STRING = "mongodb+srv://aow:aow@aow.74qmf.mongodb.net/aow?retryWrites=true&w=majority"

        # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
        client = MongoClient(CONNECTION_STRING)

        # Create the database for our example (we will use the same database throughout the tutorial
        return client['aow']

    except pymongo.errors.ServerSelectionTimeoutError as err:
        # return if cannot connect mongodb
        return -1
