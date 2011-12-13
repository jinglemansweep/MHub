"""

MHub Applications Module


.. module:: app
   :platform: Unix
   :synopsis: MHub Applications Module

.. moduleauthor:: JingleManSweep <jinglemansweep@gmail.com>

"""

import logging

from pymongo import Connection
from twisted.application.service import MultiService, Application
from twisted.internet import reactor

from service import MHubService



class MHubApp(object):

    """
    Core application container responsible for managing and running of configured plugins.

    :param cfg: Application configuration dictionary
    :type cfg: dict.
    """



    def __init__(self, cfg=None):

        """
        Constructor
        """

        self.cfg = cfg or dict()
        self.logger = logging.getLogger("app")

        self.reactor = reactor
        self.root_service = MultiService()
        self.service = MHubService(self.cfg, self.reactor, self)
        self.application = Application("mhub")
        self.root_service.setServiceParent(self.application)


    def get_application(self):

        """
        Get the Twisted application object.

        :returns: Application
        """

        return self.application


