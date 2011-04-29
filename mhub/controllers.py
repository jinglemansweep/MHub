
import datetime
import imp
import os
import time
import yaml

from carrot.connection import BrokerConnection
from carrot.messaging import Consumer, Publisher
from pprint import pprint

from dao import DefaultStore
from utils import configurator
import helpers as ctx_helpers


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


        self.process_event(message)
        message.ack()


    def update_env(self):

        """ Update read-only environment with useful data (datetime etc.) """

        dt = datetime.datetime.now()

        env = {}
        env["datetime"] = {"year": dt.year, "month": dt.month, "day": dt.day,
                           "hour": dt.hour, "minute": dt.minute, "second": dt.second}
        
        self.env = env


    def process_event(self, message=None):

        """ Process generic events using configured scripts """

        self.update_env()
        
        if not self.initialised:
            scripts = self.on_init
            self.initialised = True
        elif message is not None:
            scripts = self.on_message
        else:
            scripts = self.on_tick

        ctx = {
            "state": self.state,
            "env": self.env,
            "message": message,
            "helpers": {
                "send_email": ctx_helpers.send_email,
                "send_message": self.send_message
            }
        }

        for script in scripts:
            if os.path.exists(script):
                execfile(script, ctx)
            else:
                print "Script '%s' not found" % (script)

        self.state = ctx.get("state")
        self.env = ctx.get("env")

        self.process_actions()


    def process_actions(self):

        """ Process actions registered during JavaScript evaluation """

        actions = []

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
            self.process_event()
            print self.state
            time.sleep(0.1)


