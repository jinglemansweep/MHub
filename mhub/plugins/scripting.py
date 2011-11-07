import os


from base import BasePlugin

class ScriptingPlugin(BasePlugin):

    """
    High level JavaScript control plugin.

    :param name: Name of plugin.
    :type name: str.
    :param cls: Class/type of plugin.
    :type cls: str.
    :param service: Container service.
    :type service: mhub.service.
    :param cfg: Plugin configuration dictionary.
    :type cfg: dict.
    """

    def __init__(self, name, cls, service, cfg):

        try:
            import spidermonkey
        except ImportError:
            return

        BasePlugin.__init__(self, name, cls, service, cfg)

        self.jsrt = spidermonkey.Runtime()
        self.jsctx = self.jsrt.new_context()
        self.jsctx.add_global("publish_event", self.js_publish_event)
        self.jsctx.add_global("log", self.js_log)
        self.jsctx.add_global("clear_env", self.js_clear_env)

        self.env = dict()
        self.scripts = dict()
        self.invalid_scripts = set()
        
        self.load_scripts()
        

    def process_message(self, msg):

        """
        Service message process callback function.

        :param msg: Message dictionary.
        :type msg: dict.
        """

        self.jsctx.add_global("env", self.env)
        self.jsctx.add_global("msg", msg)

        for filename, body in self.scripts.iteritems():
            try:
                self.jsctx.execute(body)
            except:
                self.invalid_scripts.add(filename)
            try:
                self.invalid_scripts.remove(filename)
            except KeyError, e:
                pass
            self.env = self.jsctx.execute("env;")


    def load_scripts(self):

        """
        Load configured JavaScripts and register periodic reloading callbacks.
        """

        reload_interval = self.cfg.get("reload_interval", 60)

        scripts = self.cfg.get("scripts", list())
        for path in scripts:
            filename = os.path.expanduser(path)
            if filename in self.invalid_scripts:
                continue
            if not os.path.exists(filename):
                self.logger.debug("Script '%s' not found" % (filename))
                continue
            fh = open(filename, "r")
            body = fh.read()
            fh.close()
            if body != self.scripts.get(filename, ""):
                self.logger.debug("Loaded script '%s'" % (filename))
                self.scripts[filename] = body

        self.service.reactor.callLater(reload_interval, self.load_scripts)


    def js_log(self, msg):

        """
        JavaScript logger wrapper function.

        :param msg: Message to log.
        :type msg: str.
        """

        self.logger.info("JS: %s" % (msg))


    def js_publish_event(self, name, detail=None):

        """
        JavaScript event publishing wrapper function.

        :param name: Name of event.
        :type name: str.
        :param detail: Detail dictionary.
        :type detail: dict.
        """

        name = self.js_to_python(name)
        detail = self.js_to_python(detail)
        self.publish_event(name, detail)


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
            obj = obj.replace('"', '\\"').replace('\n', '\\n') \
                .replace('\r', '\\r').replace('\t', '\\t')
            return ''.join(['"', obj, '"'])
        # everything else
        else:
            return unicode(obj)