from __future__ import division
import json
import logging
import math
import urllib2
import pprint
from twisted.internet.protocol import Protocol, Factory
from twisted.internet.task import LoopingCall
from twisted.application.internet import TCPServer
from twisted.web.client import getPage

from base import BasePlugin


class EmailPlugin(BasePlugin):

    """
    IMAP Email Plugin
    """

    def __init__(self, name, cls, service, cfg):

        """ 
        Constructor 

        :param name: Name of plugin.
        :type name: str.
        :param cls: Class/type of plugin.
        :type cls: str.
        :param service: Container service.
        :type service: mhub.service.
        :param cfg: Plugin configuration dictionary.
        :type cfg: dict.
        """

        BasePlugin.__init__(self, name, cls, service, cfg)

        self.account = self.cfg.get("account", dict())

        
        # if self.feed is None:
        #     self.logger.warn("No feed configured")
        #     return

        # poll_task = LoopingCall(self.poll_feed)
        # poll_task.start(self.cfg.get("poll_interval", 60))

    

        
