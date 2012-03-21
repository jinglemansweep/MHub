import logging
from socket import socket, AF_INET, SOCK_DGRAM
from twisted.internet.protocol import DatagramProtocol, Factory
from twisted.internet import reactor

from base import BasePlugin


class ByeByeStandbyPlugin(BasePlugin):

    """
    ByeByeStandby home automation plugin.
    """

    default_config = {
        "enabled": False,
        "host": "192.168.0.100",
        "port_receive": 53007,
        "port_send": 53008,
        "blacklist": [
            "Connecting to",
            "DHCP Bound to",
            "Resolving server address:",
            "No reply, closing socket.",
            "Closing socket",
            "Timeout:TCP connection",
            "Sent heartbeat",
            "Z:OK:E"
        ]
    }


    def setup(self, cfg):

        BasePlugin.setup(self, cfg)

        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.protocol = ByeByeStandbyProtocol()
        self.protocol.plugin = self

        self.port = self.cfg.get("port_receive", 53007)
        self.blacklist = self.cfg.get("blacklist", [])

        reactor.listenUDP(self.port, self.protocol)

	self.subscribe(self.switch_device, "%s.%s.switch" % (self.cls, self.name))


    def switch_device(self, signal, detail):

        """
        Device switcher callback.

        :param msg: Message dictionary.
        :type msg: dict.
        """

        frequency = detail.get("frequency", 3)

        state = 1 if detail.get("state", False) else 0
        device = detail.get("device")
        host = self.cfg.get("host")
        port = self.cfg.get("port_send", 53008)
        if device and host:
            h, u = device[0], device[1:]
            cmd = "D:%i%s%02d:E" % (int(state), h.upper(), int(u))
            for _ in xrange(frequency):
                self.socket.sendto(cmd, (host, port))



class ByeByeStandbyProtocol(DatagramProtocol):

    """
    ByeByeStandby Twisted protocol
    """

    ignored_data = ["Sent heartbeat", "Z:OK:E"]

    def __init__(self):

        self.logger = logging.getLogger("plugin.protocol")

        

    def datagramReceived(self, data, (host, port)):

        """
        Data received callback function

        :param data: Data received.
        :type data: str.
        """

        for ignored in self.plugin.blacklist:
            if ignored in data: return
        
        self.plugin.publish(["a:input"], dict(data=data))


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
