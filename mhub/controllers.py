
import datetime
import os
import time
import yaml

from carrot.connection import BrokerConnection
from carrot.messaging import Consumer, Publisher
from pymongo import Connection
from spidermonkey import Runtime
from pprint import pprint

from dao import DefaultStore
from providers import SqueezeboxServerProvider
from utils import configurator
from utils import JSBridge


class MainController(object):


    mq = None
    providers = None
    state = None


    def __init__(self, cfg):

        self.cfg = self.load_configuration()
        self.callbacks = {"on_message": []}
        self.state = dict()

        self.setup_scripts()
        self.setup_messaging()
        self.setup_interpreter()
        self.setup_persistence()


    def load_configuration(self):
        
        return configurator()


    def setup_persistence(self, host="localhost", port=27017):
        
        self.store = DefaultStore(host=host, port=port)

            
    def setup_messaging(self, host="localhost", 
                              port=5672, 
                              user="guest", 
                              password="guest", 
                              vhost=None):

        self.mq_connection = BrokerConnection(hostname=host, 
                                              port=port, 
                                              userid=user, 
                                              password=password, 
                                              virtual_host=vhost)

        self.mq_consumer = Consumer(connection=self.mq_connection, 
                                    queue="input", 
                                    exchange="mhub", 
                                    exchange_type="topic", 
                                    routing_key="input.*")

        self.mq_consumer.register_callback(self.mq_message_received)


    def setup_interpreter(self):
        
        self.js_runtime = Runtime()
        self.js_ctx = self.js_runtime.new_context()
        self.js_handler = JSBridge()


    def setup_scripts(self):

        print self.cfg
        scripts = self.cfg.get("scripts", dict())
        self.on_message = scripts.get("on_message", list())
        self.on_tick = scripts.get("on_tick", list())


    def send_message(self, message, 
                           exchange="mhub", 
                           key="action.default"):

        self.mq_publisher = Publisher(connection=self.mq_connection, 
                                      exchange=exchange, 
                                      exchange_type="topic",
                                      routing_key=key)

        self.mq_publisher.send(message)
        self.mq_publisher.close()


    def mq_message_received(self, data, message):

        key = data.get("key", None)

        if key is not None:
            self.process_events(self.state, data)

        message.ack()


    def update_env(self):

        dt = datetime.datetime.now()

        env = {}
        env["datetime"] = {"year": dt.year, "month": dt.month, "day": dt.day,
                           "hour": dt.hour, "minute": dt.minute, "second": dt.second}
        
        self.env = env


    def process_events(self, message=None):

        self.update_env()
        self.js_ctx.add_global("state", self.state)
        self.js_ctx.add_global("env", self.env)
        self.js_ctx.add_global("handler", self.js_handler)
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
        self.js_handler = self.js_ctx.execute("handler;")        
        
        self.process_actions()


    def process_actions(self):

        actions = self.js_handler.actions

        for action in actions:

            action = dict(action)
            provider = action.get("provider", "default")
            cmd = action.get("cmd")            
            device = action.get("device", "default")
            params = action.get("params", dict())

            if all([provider, cmd]):
                message = {"cmd": cmd, "device": device, "params": params}
                self.send_message(message, key="action.%s" % (provider))
                print "Processing action '%s'" % (action)

            actions.pop()


    def start(self):

        while True:

            self.mq_consumer.fetch(enable_callbacks=True)
            self.process_events()
            print self.state
            time.sleep(0.1)
