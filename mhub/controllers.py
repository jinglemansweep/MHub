
import datetime
import os
import yaml

from carrot.connection import BrokerConnection
from carrot.messaging import Consumer, Publisher
from pymongo import Connection
from spidermonkey import Runtime
from pprint import pprint

from providers import SqueezeboxServerProvider
from utils import load_configuration

class MainController(object):

    mq = None
    providers = None

    def __init__(self, cfg):

        self.cfg = self.load_configuration()
        self.callbacks = {"on_message": []}

        self.setup_scripts()
        self.setup_messaging()
        self.setup_interpreter()
        self.setup_persistence()


    def load_configuration(self):
        
        return load_configuration()

    def setup_persistence(self, host="localhost", port=27017):
        
        self.db_connection = Connection(host, port)
        self.db = self.db_connection["mhub"]
        self.state = self.db.metadata.find_one({"_id": "state"})
        if self.state is None:
            self.state = self.db.metadata.insert({"_id": "state"})

            
    def setup_messaging(self, host="localhost", port=5672, user="guest", password="guest", vhost=None):

        self.mq_connection = BrokerConnection(hostname=host, port=port, userid=user, password=password, virtual_host=vhost)
        self.mq_consumer = Consumer(connection=self.mq_connection, queue="input", exchange="mhub", routing_key="event.default")
        self.mq_consumer.register_callback(self.mq_message_received)


    def setup_interpreter(self):
        
        self.js_runtime = Runtime()
        self.js_ctx = self.js_runtime.new_context()


    def setup_scripts(self):

        print self.cfg
        scripts = self.cfg.get("scripts", dict())
        self.on_message = scripts.get("on_message", list())
        self.on_tick = scripts.get("on_tick", list())
        

    def send_message(self, message, exchange="mhub", key="event.default"):

        self.mq_publisher = Publisher(connection=self.mq_connection, exchange=exchange, routing_key=key)
        self.mq_publisher.send(message)
        self.mq_publisher.close()


    def mq_message_received(self, data, message):

        key = data.get("key", None)

        if key is not None:
            self.process_events(self.state, data)

        message.ack()


    def update_state(self):

        dt = datetime.datetime.now()

        self.state["datetime"] = {"year": dt.year, "month": dt.month, "day": dt.day,
                                  "hour": dt.hour, "minute": dt.minute, "second": dt.second}


    def process_events(self, message=None):

        self.update_state()
        self.js_ctx.add_global("state", self.state)
        self.js_ctx.add_global("message", message)

        if message:
            scripts = self.on_message
        else:
            scripts = self.on_tick

        for script in scripts:
            if os.path.exists(script):
                fh = file(script, "r")
                content = "\n".join(fh.readlines())
                fh.close()
                processed = self.js_ctx.execute(content)
            else:
                print "Script not found"

        self.state = self.js_ctx.execute("state;")
        print self.state

        
    def start(self):

        while True:
            self.mq_consumer.process_next()
            self.process_events()