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
from pymongo.errors import AutoReconnect
from mongoengine import connect
from twisted.application.service import Service
from twisted.internet import reactor, threads

from plugins.amqp import AmqpPlugin
from plugins.byebyestandby import ByeByeStandbyPlugin
from plugins.echo import EchoPlugin
from plugins.email import EmailPlugin
from plugins.http import HttpPlugin
from plugins.latitude import LatitudePlugin
from plugins.mpd_client import MpdPlugin
from plugins.scheduler import SchedulerPlugin
from plugins.scripting import ScriptingPlugin
from plugins.telnet import TelnetPlugin
from plugins.test import TestPlugin
from plugins.twitter_client import TwitterPlugin
from plugins.web import WebPlugin
from plugins.xmpp import XmppPlugin

from persistence import StateItem


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
        "scheduler": SchedulerPlugin,
        "scripting": ScriptingPlugin,
        "telnet": TelnetPlugin,
        "test": TestPlugin,
        "twitter": TwitterPlugin,
        "web": WebPlugin,
        "xmpp": XmppPlugin
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

            connect("mhub", host=store_host, port=store_port)

            service_cfg = StateItem(name="app.!config", value=json.dumps(app_cfg))
            service_cfg.save()

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


    def publish(self, signal, detail, plugin):

        """
        Publish event to service
        """

        fq_signal = "%s.%s.%s" % (plugin.cls, plugin.name, signal)
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


