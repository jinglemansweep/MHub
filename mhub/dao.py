
from datetime import datetime
from pymongo import Connection


class DefaultStore(object):


    db_host = None
    db_port = None
    db_connection = None
    db = None


    def __init__(self, host="localhost", port=27017):

        self.db_host = host
        self.db_port = port


    def setup(self):

        self.db_connection = Connection(host, port)
        self.db = self.db_connection["mhub"]
        self.state = self.db.metadata.find_one({"_id": "state"})
        if self.state is None:
            self.state = self.db.metadata.insert({"_id": "state"})


    def set_state(self, key, data=None, duration=0):

        db_key = "state_%s" % (key)
        db_payload = {
            "_id": db_key,
            "data": data,
            "created": datetime.now(),
            "duration": duration
        }

        record = self.db.metadata.find_one({"_id": db_key})

        if record is None:
            self.db.metadata.insert(db_payload)


    def get_state(self, key, default=None):

        db_key = "state_%s" % (key)

        record = self.db.metadata.find_one({"_id": db_key})

        if record is not None:
            return record
        else:
            return default
        
