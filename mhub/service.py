"""

MHub Services Module

.. module:: service
   :platform: Unix
   :synopsis: MHub Services Module

.. moduleauthor:: JingleManSweep <jinglemansweep@gmail.com>

"""

import fnmatch
import json
import logging
import pprint
import sys

from pymongo import Connection
from pymongo.objectid import ObjectId
from pymongo.errors import AutoReconnect
from twisted.application.service import Service
from twisted.internet import reactor, threads

from plugins.amqp import AmqpPlugin
from plugins.byebyestandby import ByeByeStandbyPlugin
from plugins.echo import EchoPlugin
from plugins.email import EmailPlugin
from plugins.http import HttpPlugin
from plugins.latitude import LatitudePlugin
from plugins.mpd_client import MpdPlugin
from plugins.pubnub import PubnubPlugin
from plugins.scheduler import SchedulerPlugin
from plugins.scripting import ScriptingPlugin
from plugins.telnet import TelnetPlugin
from plugins.test import TestPlugin
from plugins.tivo import TivoPlugin
from plugins.twitter_client import TwitterPlugin
from plugins.web import WebPlugin
from plugins.xmpp import XmppPlugin
from plugins.zmq import ZmqPlugin

class BaseService(Service):


    """
    Core service which manages all plugins, factories and protocols and any communications between them.

    :param cfg: Service configuration object
    :type cfg: dict.
    :param reactor: Twisted Reactor object
    :type reactor: twisted.internet.reactor
    """

    _class_map = {
        "amqp": AmqpPlugin,
        "byebyestandby": ByeByeStandbyPlugin,
        "echo": EchoPlugin,
        "email": EmailPlugin,
        "http": HttpPlugin,
        "latitude": LatitudePlugin,
        "mpd": MpdPlugin,
        "pubnub": PubnubPlugin,
        "scheduler": SchedulerPlugin,
        "scripting": ScriptingPlugin,
        "telnet": TelnetPlugin,
        "test": TestPlugin,
        "tivo": TivoPlugin,
        "twitter": TwitterPlugin,
        "web": WebPlugin,
        "xmpp": XmppPlugin,
        "zmq": ZmqPlugin
    }


    def __init__(self,
                 cfg=None,
                 reactor=None,
                 app=None):

        """ Constructor """

        cfg = cfg or dict()
        self.reactor = reactor
        self.app = app
        self.logger = logging.getLogger("mhub.service")
        self.cfg = cfg
        self.plugins = dict()
        self.metadata = dict()
        self.subscriptions = list()

        self.setup_persistence()
        self.setup_plugins()


    def setup_persistence(self):

        """
        Initialise all persistence components
        """

        self.logger.info("Initialising persistence")

        app_cfg = self.cfg.get("app")

        store_host = app_cfg.get("general").get("store_host", "localhost")
        store_port = app_cfg.get("general").get("store_port", 27017)

        self.logger.debug("MongoDB: %s:%i" % (store_host, store_port))

        try:

            self.mongo_connection = Connection()
            self.mongo_db = self.mongo_connection["mhub"]
            self.store = self.mongo_db["store"]
            self.cache = self.mongo_db["cache"]

            self._db_map = dict(store=self.store,
                                cache=self.cache)

            self.db_set(self.cache, "_config", app_cfg)

        except AutoReconnect, e:
            
            self.logger.fatal("Exiting, cannot connect to MongoDB")
            sys.exit(1)


    def setup_plugins(self):

        """
        Initialise all configured and enabled plugins
        """

        self.logger.info("Registering plugins")

        app_cfg = self.cfg.get("app")
        plugins_cfg = self.cfg.get("plugins")

        for name, plugin_cfg in plugins_cfg.iteritems():

            p_cls_str = plugin_cfg.get("class").lower()
            p_cls = self._class_map.get(p_cls_str)
            p_enabled = plugin_cfg.get("enabled", False)
            if not p_enabled: continue
            p_inst = p_cls()
            p_inst.name = name
            p_inst.cls = p_cls_str
            p_inst.service = p_inst.s = self
            p_inst.logger = logging.getLogger("plugin")
            p_inst.setup(plugin_cfg)

            self.logger.debug("%s.%s registered" % (p_cls_str, name))
            
            if hasattr(p_inst, "client"):
                p_inst.client.setServiceParent(self.app.root_service)


    def publish(self, signal, detail, plugin_cls, plugin_name, raw):

        """
        Publish event to service
        """

        fq_signal = signal if raw else "%s.%s.%s" % (plugin_cls, plugin_name, signal)
        if detail is None: detail = dict()

        match_count = 0

        for sub in self.subscriptions:
            if fnmatch.fnmatch(fq_signal, sub[1]):
                func = sub[0]
                try:
                    func(fq_signal, detail)
                except Exception, e:
                    self.logger.debug("Cannot call callback '%s'" % (func.__name__))
                    self.logger.debug(e)

                match_count += 1

        self.logger.debug("Published event '%s' (%i receivers)" % (fq_signal, match_count))
        self.logger.debug("Detail: %s" % (detail))


    def subscribe(self, func, pattern=None):
    
        """
        Create a subscription to a service event based on pattern matching
        """

        if pattern is None:
            pattern = "*"

        self.logger.debug("Subscribed pattern '%s' with '%s'" % (pattern, func.__name__))
        self.subscriptions.append((func, pattern))


    def db_find(self, collection, query, scope="service"):

        """
        Retrieve value from configured database connection
        """

        db_collection = self._db_map.get(collection, self.cache)

        if query is None: query = dict()

        records = db_collection.find(query)
        if not records: return list()
        return records


    def db_find_one(self, collection, query, scope="service"):

        """
        Retrieve value from configured database connection
        """

        db_collection = self._db_map.get(collection, self.cache)

        if query is None:
            query = dict()
        elif type(query) in (str, unicode):
            query = ObjectId(query)

        print collection, query, type(query)

        record = db_collection.find_one(query)
        return record



    def db_get(self, collection, name, default=None, scope="service"):

        """
        Retrieve value from configured database connection
        """

        db_collection = self._db_map.get(collection, self.cache)

        db_name = self._db_name(name, scope)
        existing = db_collection.find_one({"name": db_name})
        
        if existing:
            return existing["value"]
        else:
            return default


    def db_set(self, collection, name, value, scope="service"):

        """
        Store value in configured database connection
        """
 
        db_collection = self._db_map.get(collection, self.cache)

        db_name = self._db_name(name, scope) 
        db_collection.update({"name": db_name}, {"name": db_name, "value": value}, upsert=True)


    def _db_name(self, name, scope="service"):

        """
        Generates scoped database record name
        """
       
        return "%s.%s" % (scope, name) 


    # Twisted overrides


    def startService(self):
        
        """
        Start the main Twisted service handler.
        """


        service.Service.startService(self)
        self.logger.info("Service started")


class MHubService(BaseService):

    """ MHub Twisted Service """

    pass


