import datetime
import time

from twisted.python import log


class Plugin(object):

    """ Heartbeat Plugin """

    name = "heartbeat"
    description = "Heartbeat plugin"
    author = "MHub"


    def on_init(self):

        self.tasks = [
            # (1.0, self.on_second),
            (60.0, self.on_minute)
        ]


    def on_second(self):

        """ On every second handler """

        self.logger.info("Heartbeat (1 sec)")


    def on_minute(self):

        """ On every minute handler """

        self.logger.info("Heartbeat (60 secs)")


