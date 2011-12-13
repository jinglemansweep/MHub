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
from plugins.twitter_client import TwitterPlugin
from plugins.web import WebPlugin
from plugins.xmpp import XmppPlugin


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

        ds_conn = Connection(store_host, store_port)
        ds_db = ds_conn["mhub"]
        self.state = ds_db["state"]
        self.store = ds_db["store"]
        # self.state.remove({})

        self.state.save({
            "_id": "app.!config",
            "value": app_cfg
        })


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
            p_inst.service = self
            p_inst.logger = logging.getLogger("plugin")
            p_inst.state = self.state
            p_inst.store = self.store
            p_inst.setup(plugin_cfg)

            self.logger.debug("%s.%s registered" % (p_cls_str, name))
            
            if hasattr(p_inst, "client"):
                p_inst.client.setServiceParent(self.app.root_service)


    def publish_event(self, signal, sender, detail, plugin):

        """
        Publish event to service
        """

        if sender is None: sender = "%s.%s" % (plugin.cls, plugin.name)
        if detail is None: detail = dict()

        match_count = 0

        for sub in self.subscriptions:
            if fnmatch.fnmatch(signal, sub.get("signal")):
                if fnmatch.fnmatch(sender, sub.get("sender")):
                    func = sub.get("func")
                    func(sub.get("signal"), sub.get("sender"), detail)
                    match_count += 1

        self.logger.debug("Published event '%s' from '%s' to %i subscriptions" % (signal, sender, match_count))
        self.logger.debug("Detail: %s" % (detail))


    def subscribe_event(self, signal, sender, func, plugin=None):
    
        """
        Create a subscription to a service event
        """

        if signal is not None:
            if plugin is not None:
                signal = "%s.%s.%s" % (plugin.cls, plugin.name, signal)
        else:
            signal = "*"
        if sender is None: sender = "*"

        self.logger.debug("Subscribed to event '%s' from '%s' using '%s'" % (signal, sender, func.__name__))
        self.subscriptions.append(dict(signal=signal, sender=sender, func=func))


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


