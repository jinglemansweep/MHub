import datetime

class Plugin(object):

    """ Echo Plugin """

    def __init__(self, cfg, publisher, logger):

        """ Constructor """

        self.cfg = cfg
        self.publisher = publisher
        self.logger = logger
        self.tasks = list()
        

    def on_message(self, data, message):

        """ On AMQP message handler """

        self.logger.debug("Echo: %s" % (message.body))


