import os
import spidermonkey
import sys

from base import BasePlugin
from persistence import StoreItem, Resource


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

        self.jsrt = spidermonkey.Runtime()
        self.jsctx = self.jsrt.new_context()
        self.jsctx.add_global("publish", self.js_publish)
        self.jsctx.add_global("log", self.js_log)
        self.jsctx.add_global("clear_env", self.js_clear_env)

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

        event = dict(signal=signal, detail=detail)

        self.jsctx.add_global("env", self.env)
        self.jsctx.add_global("event", event)

        for rid, body in self.scripts.iteritems():
            try:
                self.jsctx.execute(body)
                pass
            except Exception, e:
                self.invalid_scripts.add(rid)
                self.logger.debug(sys.exc_info()[0])
            # try:
            #     self.invalid_scripts.remove(rid)
            # except KeyError, e:
            #     pass
            self.env = self.jsctx.execute("env;")



    def load_scripts(self):

        """
        Load configured JavaScripts and register periodic reloading callbacks.
        """

        reload_interval = self.cfg.get("reload_interval", 60)
        cls = self.cfg.get("resource_class", "%s.%s" % ("plugin", self.cls))

        resources =  Resource.objects(item_class=cls)

        for resource in resources:
            if resource.name in self.invalid_scripts:
                continue
            body = resource.value
            if body != self.scripts.get(resource.name, ""):
                self.logger.debug("Loaded script '%s'" % (resource.name))
                self.logger.debug("Body: %s" % (body))
                self.scripts[resource.name] = body

        self.service.reactor.callLater(reload_interval, self.load_scripts)


    def js_log(self, msg):

        """
        JavaScript logger wrapper function.

        :param msg: Message to log.
        :type msg: str.
        """

        self.logger.info("JS: %s" % (msg))


    def js_publish(self, signal, detail=None):

        """
        JavaScript event publishing wrapper function.

        :param name: Name of event.
        :type name: str.
        :param detail: Detail dictionary.
        :type detail: dict.
        """

        if detail is None: detail = dict()

        signal = self.js_to_python(signal)
        detail = self.js_to_python(detail)
        self.publish(signal, detail)

    def js_clear_env(self):

        """
        Reset/clear JavaScript environment/context dictionary.
        """

        self.env = dict()


    def js_to_python(self, obj):

        """
        Convert JavaScript object into nested Python dictionary.

        :param obj: JavaScript object.
        :type obj: spidermonkey.Object
        :returns: Python dictionary.
        """

        obj_type = type(obj)

        if obj_type == spidermonkey.Object:
            data = []
            for k in obj:
                data.append("".join(['"', k, '"', ":", self.js_to_python(obj[k])]))
            return ''.join(['{', ','.join(data), '}'])
        # spidermonkey array
        elif obj_type == spidermonkey.Array:
            data = []
            for i in obj:
                data.append(self.js_to_python(i))
            return ''.join(['[', ','.join(data), ']'])
        # string / unicode
        elif obj_type == unicode or obj_type == str:
            obj = obj.replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
            return ''.join(['', obj, ''])
        # everything else
        else:
            return unicode(obj)
