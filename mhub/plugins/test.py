import sys

from base import BasePlugin



class TestPlugin(BasePlugin):

    """
    Test plugin.
    """

    default_config = {
        "enabled": False
    }

    def setup(self, cfg):

        BasePlugin.setup(self, cfg)
        self.subscribe(self.process_event, "*.*.new_interval")
        self.subscribe(self.process_event, "scheduler.*.*")

    def process_event(self, signal, detail):

        """
        Service message process callback.

        :param msg: Message dictionary.
        :type msg: dict.
        """

        self.logger.debug("Test: [%s] %s" % (signal, detail))
