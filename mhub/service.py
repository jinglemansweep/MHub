"""

MHub Services Module

.. module:: service
   :platform: Unix
   :synopsis: MHub Services Module

.. moduleauthor:: JingleManSweep <jinglemansweep@gmail.com>

"""

import json
import logging
import louie
from twisted.application.service import Service
from twisted.internet import reactor, threads



class BaseService(Service):


    """
    Core service which manages all plugins, factories and protocols and any communications between them.

    :param cfg: Service configuration object
    :type cfg: dict.
    :param reactor: Twisted Reactor object
    :type reactor: twisted.internet.reactor
    """


    def __init__(self,
                 cfg=None,
                 reactor=None):

        """ Constructor """

        cfg = cfg or dict()
        self.reactor = reactor
        self.logger = logging.getLogger("mhub.service")
        self.cfg = cfg
        self.plugins = dict()


    def setup(self):

        """
        Setup service.
        """

        pass


    def install_plugin(self, name, plugin):

        """
        Install plugin into service.
        """

        self.plugins[name] = plugin
        

    # Twisted overrides


    def startService(self):
        
        """
        Start the main Twisted service handler.
        """

        self.setup()
        service.Service.startService(self)
        self.logger.info("Service started")


class MHubService(BaseService):

    """ MHub Twisted Service """

    pass


