import datetime

from twisted.python import log

class Plugin(object):

    """ Echo Plugin """

    name = "echo"
    description = "Simple message echo service"
    author = "MHub"


    def on_init(self):

        

        pass
    

    def on_amqp_message(self, body):

        """ On AMQP message handler """

        self.logger.info("Echo: %s" % (body))

