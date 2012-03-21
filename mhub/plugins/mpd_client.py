import logging
from twisted.application.internet import TCPClient
from mpd import MPDProtocol, MPDFactory

from plugins.base import BasePlugin

class MpdPlugin(BasePlugin):

    """
    Music Player Daemon (MPD) plugin.
    """

    default_config = {
        "enabled": False,
        "host": "localhost",
        "port": 6600
    }


    def setup(self, cfg):

        BasePlugin.setup(self, cfg)
        
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

        self.publish(["a:status"], result)



class MpdFactory(MPDFactory):

    def __init__(self, plugin):

        self.plugin = plugin
        self.logger = logging.getLogger("plugin.factory")


    def connectionMade(self, protocol):

        protocol.status().addCallback(self.plugin.status)

