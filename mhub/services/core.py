
import datetime
import imp
import os
import random
import sys
import time
import warnings
import yaml

from kombu.connection import BrokerConnection
from kombu.messaging import Exchange, Queue, Producer, Consumer
from pprint import pprint
from socket import timeout
from twisted.application import service, internet
from twisted.internet import task, reactor, endpoints, protocol
from twisted.python import log
from twisted.python import usage
from twisted.web import server, static

from mhub.configurator import configure
from mhub.meta import PluginHelper
from mhub.services.http import HTTPService
from mhub.services.xmlrpc import XMLRPCService
from mhub.utils import Logger


class CoreService(service.Service):

    """
    Core Twisted Service Controller
    """


    mq = None
    initialised = None


    # === SERVICE INITIALISATION ===


    def __init__(self, reactor=None, options=None):

        """ Constructor """

        self.reactor = reactor
        self.options = options
        self.cfg = configure()
        self.plugins = dict()
        self.logger = Logger(name="service")
        self.initialised = False

        self.logger.info("Welcome to MHub")

            
    def setup_service(self):

        """ Setup main service """

        warnings.filterwarnings("ignore")

        self.setup_messaging()
        
        if self.options.get("server", False):
            self.setup_plugins()
            self.init_plugins()
        self.setup_reactor()


    def setup_messaging(self, consumer=True):

        """ Setup AMQP connection and message consumer """

        self.logger.info("Configuring AMQP messaging")

        general_cfg = self.cfg.get("general")
        amqp_cfg = self.cfg.get("amqp")

        amqp_host = self.options.get("host", amqp_cfg.get("host"))
        amqp_port = self.options.get("port", amqp_cfg.get("port"))

        self.mq_exchange = Exchange(name="mhub",
                                    type="fanout",
                                    durable=False)

        node_name = self.options.get("name", general_cfg.get("name"))
        queue_name = "queue-%s" % (node_name)

        self.logger.info("Queue: %s" % (queue_name))

        self.mq_queue = Queue(queue_name,
                              exchange=self.mq_exchange,
                              durable=False)

        self.mq_connection = BrokerConnection(hostname=amqp_host,
                                              port=amqp_port,
                                              userid=amqp_cfg.get("username"),
                                              password=amqp_cfg.get("password"),
                                              virtual_host=amqp_cfg.get("vhost"))

        self.mq_channel = self.mq_connection.channel()

        self.mq_consumer = Consumer(self.mq_channel,
                                    self.mq_queue)

        if consumer:
            self.mq_consumer.register_callback(self.on_message)
            self.mq_consumer.consume()
        
        self.mq_producer = Producer(channel=self.mq_channel,
                                    exchange=self.mq_exchange,
                                    serializer="json")
        

    def setup_plugins(self):

        """ Setup configured plugins """

        self.logger.info("Configuring plugins")

        base_plugins_dir = os.path.join(os.path.dirname(__file__), "..", "plugins")
        user_plugins_dir = os.path.expanduser(self.cfg.get("general").get("plugin_dir"))
        config_dir = self.cfg.get("general").get("config_dir")
        cache_dir = self.cfg.get("general").get("cache_dir")
        plugin_config_dir = os.path.join(config_dir, "plugins")
        plugin_cache_dir = os.path.join(cache_dir, "plugins")

        plugin_list = []
        plugin_list.extend([os.path.join(base_plugins_dir, p) \
                            for p in os.listdir(base_plugins_dir) \
                            if p.endswith(".py")])
        plugin_list.extend([os.path.join(user_plugins_dir, p) \
                            for p in os.listdir(user_plugins_dir) \
                            if p.endswith(".py")])

        for plugin_path in plugin_list:

            basename = os.path.basename(plugin_path)
            name = basename[:-3]

            if name == "__init__": continue

            try:
                plugin_src = imp.load_source("mhub_%s" % (name), plugin_path)
                orig_cls = plugin_src.Plugin
                plugin_cls = type("Plugin", (orig_cls, PluginHelper), {})
                plugin_inst = plugin_cls()
            except ImportError, e:
                self.logger.error("Plugin '%s' cannot be imported" % (name))
                continue
            except IOError, e:
                self.logger.error("Plugin '%s' not found" % (name))
                continue

            p_config_dir = os.path.join(plugin_config_dir, name)
            p_cache_dir = os.path.join(plugin_cache_dir, name)
            p_config_file = os.path.join(p_config_dir, "plugin.yml")

            if not os.path.exists(p_config_dir):
                os.makedirs(p_config_dir)

            if not os.path.exists(p_cache_dir):
                os.makedirs(p_cache_dir)

            if os.path.exists(p_config_file):
                self.logger.debug("Loading configuration for plugin '%s'" % (name))
                stream = file(p_config_file, "r")
                p_cfg = yaml.load(stream)
                if "enabled" not in p_cfg: 
                    p_cfg["enabled"] = False
            else:
                self.logger.debug("Creating default configuration for plugin '%s'" % (name))
                if hasattr(plugin_cls, "default_config"):
                    p_cfg = plugin_cls.default_config
                else:
                    p_cfg = dict()
                p_cfg["enabled"] = False
                stream = file(p_config_file, "w")
                yaml.dump(p_cfg, stream)

            plugin_logger = Logger(name="plugin.%s" % (name),
                                   producer=self.mq_producer)
            plugin_inst.logger = plugin_logger
            plugin_inst.producer = self.mq_producer
            plugin_inst.cfg = p_cfg

            if p_cfg.get("enabled"):
                self.logger.info("Registering plugin '%s'" % (name))
                self.plugins[name] = plugin_inst


    def init_plugins(self):

        """ Plugin initialisation helper """

        if not self.initialised:
            for name, plugin in self.plugins.iteritems():
                self.logger.debug("Initialising plugin '%s'" % (name))
                if hasattr(plugin, "on_init"):
                    plugin.on_init()
            self.initialised = True
            

    def setup_reactor(self):

        """ Setup Twisted reactor events and callbacks """

        self.logger.info("Configuring reactor events and callbacks")

        cfg_xmlrpc = self.cfg.get("xmlrpc", dict())
        xmlrpc_enabled = cfg_xmlrpc.get("enabled", False)
        xmlrpc_port = cfg_xmlrpc.get("port", 8081)

        if xmlrpc_enabled:

            xmlrpc_service = XMLRPCService()
            xmlrpc_service.cs = self
            self.reactor.listenTCP(xmlrpc_port, 
                                   server.Site(xmlrpc_service))

        cfg_web = self.cfg.get("web", dict())
        http_enabled = cfg_web.get("enabled", False)
        http_port = cfg_web.get("port", 8080)
        webroot_dir = cfg_web.get("webroot_dir", "")

        if http_enabled and os.path.exists(webroot_dir):

            http_service = HTTPService()
            http_service.cs = self
            http_root = static.File(webroot_dir)
            http_root.putChild("send", http_service)
            self.reactor.listenTCP(http_port,
                                   server.Site(http_root))

        cfg_general = self.cfg.get("general", dict())
        mq_poll_interval = float(cfg_general.get("poll_interval", 0.1))

        mq_task = task.LoopingCall(self.amqp_poll_message)
        mq_task.start(mq_poll_interval)

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
            self.logger.info("%i tasks declared" % (len(plugin_tasks)))


    # === AMQP MESSAGE HANDLING ===


    def amqp_poll_message(self):

        """ Poll AMQP messages """

        try:
            self.mq_connection.drain_events(timeout=0.1)
        except:
            pass


    def amqp_send_message(self, message):

        """ Send an AMQP message via configured AMQP connection """

        self.mq_producer.publish(message)


    # === MHUB EVENTS ===


    def on_message(self, data, message):

        """ On MQ message received forwarding callback function """

        for name, plugin in self.plugins.iteritems():
            if hasattr(plugin, "on_message"):
                plugin.on_message(data, message)

        message.ack()


    # === TWISTED SERVICE HANDLING ===


    def startService(self):

        """ Starts the reactor service """

        self.setup_service()

  

        


