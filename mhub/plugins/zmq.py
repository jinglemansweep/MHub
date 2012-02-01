import json
import logging
from txZMQ import ZmqFactory, ZmqEndpoint, ZmqPubConnection, ZmqSubConnection
from plugins.base import BasePlugin


class ZmqPlugin(BasePlugin):

    """
    Zero Messaging Queue (ZMQ/0MQ) plugin.
    """

    default_config = {
        "enabled": False
    }


    def setup(self, cfg):

        BasePlugin.setup(self, cfg)
        
        self.factory = MZMQFactory(plugin=self)
        self.factory.plugin = self

        self.endpoint_uri = "ipc:///tmp/sock"
        self.pub_endpoint = ZmqEndpoint("bind", self.endpoint_uri)
        self.sub_endpoint = ZmqEndpoint("connect", self.endpoint_uri)
        self.pub = ZmqPubConnection(self.factory, self.pub_endpoint)
        self.sub = ZmqSubConnection(self.factory, self.sub_endpoint)
        self.sub.subscribe("")
        self.sub.gotMessage = self.on_message

        self.service.reactor.callLater(2, self.send_test_message, "subject body")

        self.subscribe(self.process_event)


    def send_test_message(self, msg):

        self.pub.publish(msg)



    def process_event(self, signal, detail):

        json_obj = dict(signal=signal, detail=detail)
        json_str = json.dumps(json_obj)

        self.pub.publish(json_str)


    def on_message(self, *args):

        self.logger.debug(args)


class MZMQFactory(ZmqFactory):

    def __init__(self, plugin):

        self.plugin = plugin
        self.logger = logging.getLogger("plugin.factory")

        ZmqFactory.__init__(self)



