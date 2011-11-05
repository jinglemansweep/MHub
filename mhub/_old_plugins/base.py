import datetime
import logging

class BasePlugin(object):


    """ Base Plugin """


    def _setup(self, name):
        self.logger = logging.getLogger("plugin")


    def send_amqp_message(self, msg):

        action = msg["action"]
        msg["action"] = "%s.%s" % (self.name, action)

        self.service.send_amqp_message(msg=msg)