
import datetime
import imp
import os
import time
import yaml

from carrot.connection import BrokerConnection
from carrot.messaging import Consumer, Publisher
from twisted.internet import task
from twisted.internet import reactor
from pprint import pprint

from logsetup import DefaultLogger
from utils import configurator



class MainController(object):


    """ Main loop and messaging controller """

    mq = None
    initialised = None


    def __init__(self, options, args, server=False):

        """ Constructor """

        self.options = options
        self.args = args
        self.cfg = self.load_configuration()
        self.plugins = dict()
        self.logger = DefaultLogger(name="mhub", verbosity=options.verbosity).get_logger()
        self.initialised = False

        self.setup_messaging()
        if server: self.setup_plugins()


    def load_configuration(self):
        
        """ Loads (or initialises and returns) configuration """

        return configurator()

            
    def setup_messaging(self):

        """ Setup AMQP connection and message consumer """

        amqp_cfg = self.cfg.get("amqp")

        self.mq_connection = BrokerConnection(hostname=amqp_cfg.get("host"),
                                              port=amqp_cfg.get("port"),
                                              userid=amqp_cfg.get("username"),
                                              password=amqp_cfg.get("password"),
                                              virtual_host=amqp_cfg.get("vhost"))

        self.mq_consumer = Consumer(connection=self.mq_connection, 
                                    queue="input", 
                                    exchange="mhub", 
                                    exchange_type="topic", 
                                    routing_key="input.*")

        self.mq_publisher = Publisher(connection=self.mq_connection,
                                      exchange="mhub",
                                      exchange_type="topic",
                                      routing_key="input.default")

        self.mq_consumer.register_callback(self.on_message)


    def setup_plugins(self):

        """ Setup configured plugins """

        plugins_cfg = self.cfg.get("plugins")

        plugins_path = os.path.join(os.path.dirname(__file__), "plugins")

        for name, cfg in plugins_cfg.iteritems():
            if cfg.get("enabled"):
                self.logger.info("Plugin '%s' registered" % (name))
                self.logger.debug("Cfg: %s" % (cfg))
                plugin_path = os.path.join(plugins_path, "%s.py" % (name))
                if os.path.exists(plugin_path):
                    plugin_cls = imp.load_source("Plugin", plugin_path)
                    self.plugins[name] = plugin_cls.Plugin(cfg, self.mq_publisher, self.logger)
            else:
                self.logger.debug("Plugin '%s' disabled" % (name))


    def poll_message(self):

        """ Poll AMQP messages """

        self.mq_consumer.fetch(enable_callbacks=True)


    def send_message(self, message, key="action.default"):

        """ Send an AMQP message via configured AMQP connection """

        self.mq_publisher.send(message)


    def on_message(self, data, message):

        """ On MQ message received forwarding callback function """

        for name, plugin in self.plugins.iteritems():
            # self.logger.debug("Forwarding message to plugin '%s'" % (name))
            if hasattr(plugin, "on_message"):
                plugin.on_message(data, message)

        message.ack()


    def on_init(self):

        """ On startup forwarding function """

        if not self.initialised:
            for name, plugin in self.plugins.iteritems():
                self.logger.debug("Initialising plugin '%s'" % (name))
                if hasattr(plugin, "on_init"):
                    plugin.on_init()
            self.initialised = True
            

    def start(self):

        """ Start the main controller loop """

        self.logger.info("Controller started")

        self.on_init()

        mq_task = task.LoopingCall(self.poll_message)
        mq_task.start(0.1)

        for plugin_name, plugin_inst in self.plugins.iteritems():
            if not hasattr(plugin_inst, "tasks"): continue
            plugin_tasks = plugin_inst.tasks
            for plugin_task in plugin_tasks:
                self.logger.debug("Registered '%s' from '%s' every %.2f seconds" % (plugin_task[1].__name__,
                                                                                  plugin_name,
                                                                                  plugin_task[0]))
                task_obj = task.LoopingCall(plugin_task[1])
                task_obj.start(plugin_task[0])

        reactor.run()
