import json
import logging
from twisted.internet.protocol import Protocol, Factory
from twisted.application.internet import TCPServer

from base import BasePlugin




class TelnetPlugin(BasePlugin):

    """
    Simple telnet plugin.
    """

    default_config = {
        "enabled": False,
        "port": 9999
    }

    def setup(self, cfg):

        BasePlugin.setup(self, cfg)

        self.factory = TelnetFactory(plugin=self)
        self.factory.plugin = self

        self.client = TCPServer(self.cfg.get("port", 9999),
                                self.factory)


class TelnetProtocol(Protocol):

    """
    Simple Twisted telnet protocol
    """

    def dataReceived(self, data):

        """
        Data received callback function

        :param data: Data received.
        :type data: str.
        """

        try:
            data = json.loads(data)
        except Exception, e:
            print e
            pass

        self.factory.plugin.publish(data)
        #self.factory.plugin.publish_event("input", data)


class TelnetFactory(Factory):

    """
    Simple Twisted telnet factory

    :param plugin: Plugin instance
    :type plugin: base.Plugin.
    """

    protocol = TelnetProtocol

    def __init__(self, plugin):

        self.plugin = plugin
        self.logger = logging.getLogger("plugin.factory")
