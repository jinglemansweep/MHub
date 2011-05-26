
import datetime
import imp
import os
import time
import yaml

from kombu.connection import BrokerConnection
from kombu.messaging import Exchange, Queue, Producer, Consumer
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

        amqp_host = self.options.host if hasattr(self.options, "host") else amqp_cfg.get("host")
        amqp_port = self.options.port if hasattr(self.options, "port") else amqp_cfg.get("port")

        self.mq_exchange = Exchange("mhub",
                                    "topic",
                                    durable=False,
                                    auto_delete=True)
        
        self.mq_queue = Queue("input",
                              exchange=self.mq_exchange,
                              key="input.*")

        self.mq_connection = BrokerConnection(hostname=amqp_host,
                                              port=amqp_port,
                                              userid=amqp_cfg.get("username"),
                                              password=amqp_cfg.get("password"),
                                              virtual_host=amqp_cfg.get("vhost"))

        self.mq_channel = self.mq_connection.channel()

        self.mq_consumer = Consumer(self.mq_channel, self.mq_queue)

        self.mq_consumer.register_callback(self.on_message)
        
        self.mq_producer = Producer(self.mq_channel,
                                    exchange=self.mq_exchange,
                                    serializer="json")
        

    def setup_plugins(self):

        """ Setup configured plugins """

        plugins_cfg = self.cfg.get("plugins")

        base_plugins_path = os.path.join(os.path.dirname(__file__), "plugins")
        user_plugins_path = os.path.expanduser(self.cfg.get("general").get("plugins_path"))

        for name, cfg in plugins_cfg.iteritems():
            if cfg.get("enabled"):
                self.logger.info("Plugin '%s' registered" % (name))
                self.logger.debug("Cfg: %s" % (cfg))
                plugin_filename = "%s.py" % (name)
                plugin_path = os.path.join(user_plugins_path, plugin_filename)
                if not os.path.exists(plugin_path):
                    plugin_path = os.path.join(base_plugins_path, plugin_filename)
                if os.path.exists(plugin_path):
                    plugin_cls = imp.load_source("Plugin", plugin_path)
                    self.plugins[name] = plugin_cls.Plugin(cfg, self.mq_producer, self.logger)
                else:
                    self.logger.debug("Plugin '%s' not found" % (name))
            else:
                self.logger.debug("Plugin '%s' disabled" % (name))


    def poll_message(self):

        """ Poll AMQP messages """

        message = self.mq_consumer.queues[0].get()
        if message:
            self.mq_consumer.receive(message.payload, message)

        return message


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
        mq_task.start(0.01)

        for plugin_name, plugin_inst in self.plugins.iteritems():
            if not hasattr(plugin_inst, "tasks"): continue
            plugin_tasks = plugin_inst.tasks
            for plugin_task in plugin_tasks:
                interval = plugin_task[0]
                func = plugin_task[1]
                self.logger.debug("Registered '%s' from '%s' every %.2f seconds" % (func.__name__,
                                                                                  plugin_name,
                                                                                  interval))
                task_obj = task.LoopingCall(func)
                task_obj.start(interval)

        reactor.run()
