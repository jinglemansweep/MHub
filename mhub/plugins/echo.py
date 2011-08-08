import datetime

from twisted.python import log


class Plugin(object):

    """ Echo Plugin """

    name = "echo"
    description = "Simple message echo service"
    author = "MHub"


    def on_init(self):

        pass
    

    def on_message(self, data, message):

        """ On AMQP message handler """

        print "HELLO"
        log.msg("Echo: %s" % (message.body))


