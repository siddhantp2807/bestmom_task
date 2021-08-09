import pymongo

class Manager :

    def __init__(self, db_name, collection) :
        self.client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
        self.db = self.client[db_name]
        self.collection = self.db[collection]

    def add_record(self, data) :

        key = { "name" : data["name"] }
        self.collection.update(key, data, upsert=True)

    def find_records(self, keys) :
        
        returned = self.collection.find(keys, { "_id" : 0 })

        return returned

