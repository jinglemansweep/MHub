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

    default_config = {
        "enabled": False
    }

    def setup(self, cfg):

        BasePlugin.setup(self, cfg)

        self.account = self.cfg.get("account", dict())


    

        
