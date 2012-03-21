import logging
from oauth import oauth
from twisted.internet import defer, task
from twisted.internet.task import LoopingCall
from twisted.web.client import getPage

from base import BasePlugin


class HttpPlugin(BasePlugin):

    """
    HTTP page downloader plugin.
    """

    default_config = {
        "url": "http://en.wikipedia.org",
        "patterns": ["welcome to"],
        "poll_interval": 60
    }
    

    def setup(self, cfg):

        BasePlugin.setup(self, cfg)
        
        self.url = self.cfg.get("url", None)
        self.patterns = self.cfg.get("patterns", list())

        if self.url is None:
            self.logger.debug("URL not specified.")
            return

        poll_task = LoopingCall(self.poll_url)
        poll_task.start(self.cfg.get("poll_interval", 60))


    def poll_url(self):
        
        """
        Retrieves HTML content from configured URL.
        """

        getPage(self.url).addCallbacks(callback=self.process_response,
                                       errback=self.error_response)


    def process_response(self, body):

        """
        Callback function used to search the retrieved HTML for the configured patterns.
        """

        found = False
        matches = list()

        for pattern in self.patterns:
            if pattern.lower() in str(body).lower():
               found = True
               matches.append(pattern.lower())

        if found:                  
            detail = dict(url=self.url,
                          matches=matches)
            self.publish(["a:match"], detail)


    def error_response(self, detail):

        """
        Callback function used when page retrieval fails.
        """

        self.logger.debug("Cannot poll requested URL: %s" % (detail))





