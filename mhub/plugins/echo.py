import louie
from base import BasePlugin



class EchoPlugin(BasePlugin):

    """
    Simple echo plugin.

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

        louie.connect(self.process_event)


    def process_event(self, detail, signal, sender):

        """
        Service message process callback.

        :param msg: Message dictionary.
        :type msg: dict.
        """
        
        self.logger.debug("Echo: %s > %s" % ((sender, signal), detail))
