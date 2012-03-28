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
        self.subscribe(self.process_event)


    def process_event(self, tags, detail):

        """
        Service message process callback.

        :param msg: Message dictionary.
        :type msg: dict.
        """

        self.logger.debug(",".join(tags))
        self.logger.debug(detail)
