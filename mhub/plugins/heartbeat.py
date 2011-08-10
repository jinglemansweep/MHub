import datetime

from twisted.python import log


class Plugin(object):

    """ Heartbeat Plugin """

    name = "heartbeat"
    description = "Heartbeat plugin"
    author = "MHub"


    def on_init(self):

        self.tasks = [(1.0, self.on_second)]


    def on_second(self):

        """ On every second  handler """

        log.msg("Second has elapsed")


