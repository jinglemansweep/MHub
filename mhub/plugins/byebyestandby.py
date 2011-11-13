import logging
from socket import socket, AF_INET, SOCK_DGRAM
from twisted.internet.protocol import DatagramProtocol, Factory
from twisted.internet import reactor

from base import BasePlugin


class ByeByeStandbyPlugin(BasePlugin):

    """
    ByeByeStandby home automation plugin.

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

        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.protocol = ByeByeStandbyProtocol()
        self.protocol.plugin = self

        port = self.cfg.get("port_receive", 53007)

        reactor.listenUDP(port, self.protocol)


    def process_message(self, msg):

        """
        Service message process callback.

        :param msg: Message dictionary.
        :type msg: dict.
        """

        msg_type = msg.get("type")
        event = msg.get("event")
        detail = msg.get("detail")

        if msg_type == "event" and event == "switch":
            state = 1 if detail.get("state", False) else 0
            device = detail.get("device")
            host = self.cfg.get("host")
            port = self.cfg.get("port_send", 53008)
            if device and host:
                h, u = device[0], device[1:]
                cmd = "D:%i%s%02d:E" % (int(state), h.upper(), int(u))
                self.socket.sendto(cmd, (host, port))



class ByeByeStandbyProtocol(DatagramProtocol):

    """
    ByeByeStandby Twisted protocol
    """

    def datagramReceived(self, data, (host, port)):

        """
        Data received callback function

        :param data: Data received.
        :type data: str.
        """

        print data
        #self.plugin.publish_event("input", dict(data=data))




class ByeByeStandbyFactory(Factory):

    """
    ByeByeStandby Twisted factory

    :param plugin: Plugin instance
    :type plugin: base.Plugin.
    """

    protocol = ByeByeStandbyProtocol

    def __init__(self, plugin):

        self.plugin = plugin
        self.logger = logging.getLogger("plugin.factory")
