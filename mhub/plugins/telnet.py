import logging
from twisted.internet.protocol import Protocol, Factory
from twisted.application.internet import TCPServer

from base import BasePlugin




class TelnetPlugin(BasePlugin):

    """
    Simple telnet plugin.

    :param name: Name of plugin.
    :type name: str.
    :param cls: Class/type of plugin.
    :type cls: str.
    :param service: Container service.
    :type service: mhub.service.
    :param cfg: Plugin configuration dictionary.
    :type cfg: dict.
    """

    def __init__(self, name, cls, service, cfg):

        BasePlugin.__init__(self, name, cls, service, cfg)

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

        self.factory.plugin.publish_event("input", dict(data=data))


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
