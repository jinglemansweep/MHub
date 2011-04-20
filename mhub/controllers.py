
import datetime
import os
import time
import yaml

from carrot.connection import BrokerConnection
from carrot.messaging import Consumer, Publisher
from pymongo import Connection
from spidermonkey import Runtime, JSError
from pprint import pprint

from dao import DefaultStore
from providers import SqueezeboxServerProvider
from utils import configurator
from utils import JSBridge


class MainController(object):


    """ Main loop and messaging controller """


    mq = None
    providers = None
    state = None
    initialised = None


    def __init__(self, cfg):

        """ Constructor """

        self.cfg = self.load_configuration()
        self.callbacks = {"on_message": []}
        self.state = dict()
        self.initialised = False

        self.setup_scripts()
        self.setup_messaging()
        self.setup_interpreter()
        self.setup_persistence()


    def load_configuration(self):
        
        """ Loads (or initialises and returns) configuration """

        return configurator()


    def setup_persistence(self, host="localhost", port=27017):

        """ Setup persistence datastore """
        
        self.store = DefaultStore(host=host, port=port)

            
    def setup_messaging(self, host="localhost", 
                              port=5672, 
                              user="guest", 
                              password="guest", 
                              vhost=None):

        """ Setup AMQP connection and message consumer """

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
        
        """ Setup JavaScript (SpiderMonkey) interpreter """

        self.js_runtime = Runtime()
        self.js_ctx = self.js_runtime.new_context()
        self.js_handler = JSBridge()


    def setup_scripts(self):

        """ Setup configured init, timed and event JavaScript scripts """

        scripts = self.cfg.get("scripts", dict())
        self.on_init = scripts.get("on_init", list())
        self.on_message = scripts.get("on_message", list())
        self.on_tick = scripts.get("on_tick", list())


    def send_message(self, message, 
                           exchange="mhub", 
                           key="action.default"):

        """ Send an AMQP message via configured AMQP connection """

        self.mq_publisher = Publisher(connection=self.mq_connection, 
                                      exchange=exchange, 
                                      exchange_type="topic",
                                      routing_key=key)

        self.mq_publisher.send(message)
        self.mq_publisher.close()


    def mq_message_received(self, data, message):

        """ On MQ message received callback function """

        key = data.get("key", None)

        if key is not None:
            self.process_events(self.state, data)

        message.ack()


    def update_env(self):

        """ Update read-only environment with useful data (datetime etc.) """

        dt = datetime.datetime.now()

        env = {}
        env["datetime"] = {"year": dt.year, "month": dt.month, "day": dt.day,
                           "hour": dt.hour, "minute": dt.minute, "second": dt.second}
        
        self.env = env


    def process_events(self, message=None):

        """ Process generic events using configured JavaScript scripts """

        self.update_env()
        self.js_ctx.add_global("state", self.state)
        self.js_ctx.add_global("env", self.env)
        self.js_ctx.add_global("handler", self.js_handler)
        self.js_ctx.add_global("message", message)

        if not self.initialised:
            scripts = self.on_init
            self.initialised = True
        elif message:
            scripts = self.on_message
        else:
            scripts = self.on_tick

        for script in scripts:
            if os.path.exists(script):
                fh = file(script, "r")
                content = "\n".join(fh.readlines())
                fh.close()
                try:
                    processed = self.js_ctx.execute(content)
                except JSError as exc:
                    print "[%s] JS execution problem: %s" % (script, exc)
            else:
                print "Script '%s' not found" % (script)

        self.state = self.js_ctx.execute("state;")
        self.js_handler = self.js_ctx.execute("handler;")        
        
        self.process_actions()


    def process_actions(self):

        """ Process actions registered during JavaScript evaluation """

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

        """ Start the main controller loop """

        while True:

            self.mq_consumer.fetch(enable_callbacks=True)
            self.process_events()
            print self.state
            time.sleep(0.1)


