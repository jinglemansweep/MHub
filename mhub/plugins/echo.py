import louie
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
        
        louie.connect(self.process_event)


    def process_event(self, detail, signal, sender, cls):

        """
        Service message process callback.

        :param msg: Message dictionary.
        :type msg: dict.
        """
        
        self.logger.debug("Echo: %s.%s [%s] %s" % (cls, sender, signal, detail))
