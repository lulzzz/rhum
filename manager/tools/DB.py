import json
from datetime import datetime, timedelta
import pymongo
from bson import json_util

class CircularDB:
    """
    CircularDB Class
    """
    def __init__(self, name='default', address="127.0.0.1", port=27017, errors_collection="errors", data_collection="data", cutoff_hours=336):
        self.name = name
        self.address = address
        self.port = port
        self.cutoff_hours = cutoff_hours
        self.client = pymongo.MongoClient(self.address, self.port)
        self.database = self.client[self.name]
        self.data_collection = self.database[data_collection]
        self.errors_collection = self.database[errors_collection]

    ## Query Samples in Range to JSON-file
    def query_db(self, days, node, series, uid):
        result = []
        for d in range(days):
            date = datetime.now() - timedelta(days = d)
            for name in self.database.collection_names():
                if not name == 'system.indexes':
                    matches = self.data_collection.find({'type':query_type})
                    for doc in matches:
                        result.append(doc)
        return result
    
    ## Dump tp JSON
    def dump_json(self, filepath, days=1, datetime_format="%Y-%m-%d %H:%M:%S"):
        try:
            self.now = datetime.now()
            self.then = self.now - timedelta(days=days)
            with open(filepath, 'w') as jsonfile:
                results = [doc for doc in self.data_collection.find({'time': {'$gte': self.then, '$lt': self.now}})]
                for doc in results:
                    del doc['_id']
                    doc['time'] = datetime.strftime(doc['time'], datetime_format)
                dump = json_util.dumps(results, indent=4)
                jsonfile.write(dump)
        except Exception as e:
            raise e
    
    ## Dump to CSV
    def dump_csv(self, filepath, days=1, datetime_format="%Y-%m-%d %H:%M:%S"):
        try:
            self.now = datetime.now()
            self.then = self.now - timedelta(days=days)
            with open(filepath, 'w') as csvfile:
                results = self.data_collection.find({'time': {'$gte': self.then, '$lt': self.now}})
                for doc in results:
                    try:
                        doc['time'] = datetime.strftime(doc['time'], datetime_format)
                        values = [
                            doc['time'],
                            doc['nt'],
                            doc['sn'],
                            doc['id'],
                            ','.join([str(i) for i in doc['data'].values()])
                        ]
                        a = [str(v) for v in values]
                        a.append('\r\n')
                        out = ','.join(a)
                        csvfile.write(out)
                    except:
                        pass
        except Exception as e:
            raise e

    ## Clean
    def clean(self, cutoff_days=56):
        if cutoff_hours is not None:
            cutoff_hours = self.cutoff_hours
        try:
            cutoff_date = datetime.now() - timedelta(days = cutoff_days)
            self.data_collection.delete_many({"time": {"$lte": cutoff_date}})
        except Exception as e:
            raise e
            
    ## Sample
    def store(self, sample, datetime_format="%Y-%m-%d %H:%M:%S"):
        try:
            sample['time'] = datetime.now() # grab the current time-stamp for the sample
            sample_id = self.data_collection.insert(sample)
            return str(sample_id)
        except Exception as e:
            raise e
