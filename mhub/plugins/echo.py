import datetime

class Plugin(object):

    """ Echo Plugin """

    def __init__(self, cfg, producer, logger):

        """ Constructor """

        self.cfg = cfg
        self.producer = producer
        self.logger = logger
        self.tasks = list()
        

    def on_message(self, data, message):

        """ On AMQP message handler """

        self.logger.debug("Echo: %s" % (message.body))


