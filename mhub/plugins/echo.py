import datetime

class Plugin(object):

    """ Echo Plugin """

    def __init__(self, cfg, producer, logger):

        """ Constructor """

        self.name = "echo"
        self.description = "Simple message echo service"
        self.author = "MHub"
        self.cfg = cfg
        self.producer = producer
        self.logger = logger
        self.tasks = list()
        

    def on_message(self, data, message):

        """ On AMQP message handler """

        self.logger.debug("Echo: %s" % (message.body))


