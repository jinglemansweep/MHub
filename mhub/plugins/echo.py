import datetime

class Plugin(object):

    """ Echo Plugin """

    name = "echo"
    description = "Simple message echo service"
    author = "MHub"
    

    def on_message(self, data, message):

        """ On AMQP message handler """

        self.logger.debug("Echo: %s" % (message.body))


