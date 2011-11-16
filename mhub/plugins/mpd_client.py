import logging
from twisted.application.internet import TCPClient
from mpd import MPDProtocol, MPDFactory

from plugins.base import BasePlugin

class MpdPlugin(BasePlugin):

    """
    Music Player Daemon (MPD) plugin.
    
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

        self.factory = MpdFactory(plugin=self)
        self.factory.plugin = self

        self.client = TCPClient(self.cfg.get("host", "localhost"),
                                self.cfg.get("port", 6600),
                                self.factory)

    def status(self, result):

        """
        MPD status event callback.

        :param result: MPD result.
        :type result: dict.
        """

        self.publish_event("status", result)



class MpdFactory(MPDFactory):

    def __init__(self, plugin):

        self.plugin = plugin
        self.logger = logging.getLogger("plugin.factory")


    def connectionMade(self, protocol):

        protocol.status().addCallback(self.plugin.status)

