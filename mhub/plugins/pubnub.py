import json
import logging
from plugins.lib.pubnub import Pubnub

from plugins.base import BasePlugin


class PubnubPlugin(BasePlugin):

    """
    Pubnub plugin.
    """

    default_config = {
        "enabled": False,
        "publish_key": "pub-xxx",
        "subscribe_key": "sub-xxx",
        "secret_key": "secret-xxx"
    }
            

    def setup(self, cfg):


        BasePlugin.setup(self, cfg)

        self.pn = Pubnub(
            cfg.get("publish_key"),
            cfg.get("subscribe_key"),
            cfg.get("secret_key"),
            cfg.get("ssl_enabled", False)
        )
        
        self.pn.subscribe({
            "channel": cfg.get("channel", "default"),
            "connect": self.on_connect,
            "callback": self.on_message
        })

        self.subscribe(self.on_event)


    def on_event(self, tags, detail):

        """
        On event callback
        """
        if "n:%s" % (self.name) not in tags:
            self.pn.publish({
                "channel": self.cfg.get("channel"),
                "message": dict(tags=tags, detail=detail),
                "callback": lambda c: None
            })


    def on_connect(self):

        """
        On connect callback
        """

        self.logger.debug("Connected")


    def on_message(self, body):

        """
        On message callback

        :param body: Body of message.
        :type body: str.
        """

        self.publish(["a:message"], body)


