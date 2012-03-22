import json
import logging
from txZMQ import ZmqFactory, ZmqEndpoint, ZmqPubConnection, ZmqSubConnection
from plugins.base import BasePlugin


class ZmqPlugin(BasePlugin):

    """
    Zero Messaging Queue (ZMQ/0MQ) plugin.
    """

    default_config = {
        "enabled": False,
        "pub_endpoint": "tcp://*:9901",
        "sub_endpoint": "tcp://*:9901"
    }


    def setup(self, cfg):

        BasePlugin.setup(self, cfg)
        
        self.factory = MZMQFactory(plugin=self)
        self.factory.plugin = self

        self.pub_endpoint_uri = cfg.get("pub_endpoint", "tcp://*:9901")
        self.pub_endpoint = ZmqEndpoint("bind", self.pub_endpoint_uri)
        self.sub_endpoint_uri = cfg.get("sub_endpoint", "tcp://*:9901")
        self.sub_endpoint = ZmqEndpoint("connect", self.sub_endpoint_uri)
        self.pub = ZmqPubConnection(self.factory, self.pub_endpoint)
        self.sub = ZmqSubConnection(self.factory, self.sub_endpoint)
        self.sub.subscribe("")
        self.sub.gotMessage = self.on_message

        self.subscribe(self.process_event)


    def process_event(self, tags, detail):

        detail_json = str(json.dumps(detail))

        self.pub.publish(detail_json, str(" ".join(tags)))


    def on_message(self, detail, tags):

        self.logger.debug("ZMQ: [%s] %s" % (tags, detail))


class MZMQFactory(ZmqFactory):

    def __init__(self, plugin):

        self.plugin = plugin
        self.logger = logging.getLogger("plugin.factory")

        ZmqFactory.__init__(self)



