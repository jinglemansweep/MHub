import sys

from base import BasePlugin



class EchoPlugin(BasePlugin):

    """
    Simple echo plugin.
    """

    default_config = {
        "enabled": False
    }

    def setup(self, cfg):

        BasePlugin.setup(self, cfg)
        self.subscribe_event(None, None, self.process_event)


    def process_event(self, signal, sender, detail):

        """
        Service message process callback.

        :param msg: Message dictionary.
        :type msg: dict.
        """

        if signal == "*": signal = "<any>"
        if sender == "*": sender = "<any>"

        self.logger.debug("Echo: %s [%s] > %s" % (signal, sender, detail))
