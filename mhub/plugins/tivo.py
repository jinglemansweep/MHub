import json
import logging
from twisted.internet.protocol import Protocol, Factory
from twisted.application.internet import TCPClient

from base import BasePlugin




class TivoPlugin(BasePlugin):

    """
    Tivo telnet control plugin.

    (http://www.tivocommunity.com/tivo-vb/showthread.php?t=392385)
    """

    default_config = {
        "enabled": False,
        "host": "mytivo",
        "port": 31339
    }

    def setup(self, cfg):

        BasePlugin.setup(self, cfg)

        self.factory = TivoFactory(plugin=self)
        self.factory.plugin = self

        self.client = TCPClient(self.cfg.get("host", "mytivo"),
                                self.cfg.get("port", 31339),
                                self.factory)

        self.cache = dict()


class TivoProtocol(Protocol):

    """
    Simple Twisted telnet protocol
    """


    places = ["TIVO", "LIVETV", "GUIDE", "NOWPLAYING"]

    ircodes = [
        "UP", "DOWN" ,"LEFT", "RIGHT", "SELECT"
        "TIVO", "LIVETV", "THUMBSUP", "THUMBSDOWN",
        "CHANNELUP", "CHANNELDOWN", "RECORD", "DISPLAY",
        "DIRECTV", "NUM0", "NUM1", "NUM2", "NUM3", "NUM4",
        "NUM5", "NUM6", "NUM7", "NUM8", "NUM9", "ENTER",
        "CLEAR", "PLAY", "PAUSE", "SLOW", "FORWARD", "REVERSE",
        "STANDBY", "NOWSHOWING", "REPLAY", "ADVANCE",
        "DELIMITER", "GUIDE", "INFO", "WINDOW"]


    def __init__(self):

        self.logger = logging.getLogger("plugin.protocol")



    def dataReceived(self, data):

        """
        Data received callback function

        :param data: Data received.
        :type data: str.
        """

        self.process_message(data)


    def connectionMade(self):

        self.plugin.subscribe(self.process_command, "%s.%s.command" % (self.plugin.cls, self.plugin.name))


    def process_message(self, data):

        if data.startswith("CH_STATUS"):
            data_arr = data.split()
            try:
                channel = int(data_arr[1])
                status = data_arr[2]
            except:
                channel = 0
            self.factory.plugin.publish("channel", dict(channel=channel, status=status))
            self.factory.plugin.cache["channel"] = channel


    def process_command(self, signal, detail):

        action = detail.get("action", "").lower()
        command_str = ""

        if action in ["goto", "teleport"]:

            place = detail.get("place", "").upper()
            if place in self.places:
                command_str = "TELEPORT %s" % (place)

        elif action in ["channel", "setch"]:

            try:
                channel = int(detail.get("channel", ""))
                command_str = "SETCH %3i" % (channel)
            except:
                pass

        elif action in ["ircode", "sendevent"]:

            ircode = detail.get("ircode", "").upper()

            if len(ircode) and ircode in self.ircodes:
                command_str = "IRCODE %s" % (ircode)

        if len(command_str):
            self.transport.write("%s\r\n" % (str(command_str)))


class TivoFactory(Factory):

    """
    Simple Twisted telnet factory

    :param plugin: Plugin instance
    :type plugin: base.Plugin.
    """

    protocol = TivoProtocol

    def __init__(self, plugin):

        self.plugin = plugin
        self.logger = logging.getLogger("plugin.factory")



    def startedConnecting(self, connector):

        pass


    def buildProtocol(self, addr):

        protocol = TivoProtocol()
        protocol.factory = self
        protocol.plugin = self.plugin
        return protocol

