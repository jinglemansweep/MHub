
from base import BasePlugin



class EchoPlugin(BasePlugin):

    def __init__(self, name, cls, service, cfg):

        BasePlugin.__init__(self, name, cls, service, cfg)


    def process_message(self, msg):

        
        self.logger.debug("Echo: %s" % msg)
