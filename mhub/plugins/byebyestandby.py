import datetime


class Plugin(object):

    """ Logic Processor Plugin """

    def __init__(self, cfg, logger):

        """ Constructor """

        self.cfg = cfg
        self.logger = logger
        

    def on_init(self):

        """ Main plugin initialisation """

        pass
        

    def on_tick(self):

        """ On tick handler """

        pass
        

    def on_message(self, message=None):

        """ On AMQP message handler """

        self.logger.debug("BBS Message")
        self.logger.debug(message)


