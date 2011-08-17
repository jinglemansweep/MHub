import sys

from twisted.python import usage
from mhub.service import CoreService


class Options(usage.Options):

    def __init__(self):
        usage.Options.__init__(self)
        self["verbosity"] = 0

    def opt_verbose(self):
        self["verbosity"] = self["verbosity"] + 1

    def opt_quiet(self):
        self["verbosity"] = self["verbosity"] - 1

    # def opt_version(self):
    #     pass

    opt_v = opt_verbose
    opt_q = opt_quiet

    optFlags = [
        ["server", "s", "Enable server mode (initialises plugins)"]
    ]

    optParameters = [
        #["endpoint", "s", 1234, "string endpoint descriptiont to listen on, defaults to 'tcp:80'"]
    ]



def makeService(options):

    from twisted.internet import reactor
    from twisted.web import server

    service = CoreService(reactor, options)

    return service
