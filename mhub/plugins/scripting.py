import os
import spidermonkey
import sys
import traceback

from base import BasePlugin


class ScriptingPlugin(BasePlugin):

    """
    High level JavaScript control plugin.
    """

    default_config = {
        "enabled": False,
        "reload_interval": 300,
        "resource_class": [
            "plugin.scripting"
        ]
    }


    def setup(self, cfg):

        BasePlugin.setup(self, cfg)

        self.env = dict()
        self.scripts = dict()
        self.invalid_scripts = set()
        
        self.load_scripts()
        self.subscribe(self.process_event)
        

    def process_event(self, signal, detail):

        """
        Service message process callback function.

        :param msg: Message dictionary.
        :type msg: dict.
        """

        ctx = {
            "env": self.env,
            "event": {
                "signal": signal,
                "detail": detail
            },
            "publish": self.publish,
            "db_get": self.db_get,
            "db_set": self.db_set,
            "db_find": self.db_find
        }

        for rid, body in self.scripts.iteritems():
            try:
                exec(body, globals(), ctx)
            except Exception, e:
                self.logger.debug("Errors caused user script '%s' to fail" % (rid))
                traceback.print_exc()
            

    def load_scripts(self):

        """
        Load configured JavaScripts and register periodic reloading callbacks.
        """

        reload_interval = self.cfg.get("reload_interval", 60)
        cls = self.cfg.get("resource_class", "%s.%s" % ("plugin", self.cls))

        resources = self.db_find("store", {"class": "%s.%s" % (self.cls, "script")}, list())

        for resource in resources:
            if resource["name"] in self.invalid_scripts:
                continue
            name = resource["name"]
            body = resource["body"]
            if body != self.scripts.get(name, ""):
                self.logger.debug("Loaded script '%s'" % (name))
                self.logger.debug("Body: %s" % (body))
                self.scripts[name] = body

        self.service.reactor.callLater(reload_interval, self.load_scripts)


