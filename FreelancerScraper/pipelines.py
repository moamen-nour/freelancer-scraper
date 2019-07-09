# Defines the pipeline that a scraped item passes through

import pymongo

class MongoPipeline(object):

    collection_name = 'jobs'

    def __init__(self):
        self.mongo_uri = 'mongodb://localhost:27017/'
        self.mongo_db = 'freelancer'
    
    def open_spider(self, spider):
        # Connect to db
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        # Close mongoDB client
        self.client.close()

    def process_item(self, item, spider):
        # Insert scraped item (avoiding insertion of duplicates)
        self.db[self.collection_name].replace_one(dict(item) , dict(item) , upsert=True)
        return item

class DefaultValuesPipeline(object):

    def process_item(self, item, spider):
        item.setdefault('title', '')
        item.setdefault('description', '')
        item.setdefault('skills', [])
        item.setdefault('remaining_time', 0)
        item.setdefault('bid', 0)
        item.setdefault('verified', False)

        return item