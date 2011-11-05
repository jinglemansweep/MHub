import logging
from twisted.application.internet import TCPClient
from mpd import MPDProtocol, MPDFactory

from plugins.base import BasePlugin

class MpdPlugin(BasePlugin):

    def __init__(self, name, cls, service, cfg):

        BasePlugin.__init__(self, name, cls, service, cfg)

        self.factory = MpdFactory(plugin=self)
        self.factory.plugin = self

        self.client = TCPClient(self.cfg.get("host", "localhost"),
                                self.cfg.get("port", 6600),
                                self.factory)


    def process_message(self, msg):
        print "MPD"
        self.logger.debug(msg)

        
    def status(self, result):

        self.publish_event("status", result)



class MpdFactory(MPDFactory):

    def __init__(self, plugin):

        self.plugin = plugin
        self.logger = logging.getLogger("plugin.factory")


    def connectionMade(self, protocol):

        protocol.status().addCallback(self.plugin.status)

