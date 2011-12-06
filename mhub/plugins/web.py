import json
import logging
import os
from twisted.internet import reactor
from twisted.internet.protocol import Protocol, Factory
from twisted.web import static as Static, server, twcgi, script, vhost
from lib.websocket import WebSocketHandler, WebSocketSite
from twisted.web.resource import Resource
from twisted.web.wsgi import WSGIResource
from flask import Flask, g, request, render_template

from base import BasePlugin



class WebPlugin(BasePlugin):

    """
    Simple Web plugin.

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

        BasePlugin.__init__(self, name, cls, service, cfg)

        self.tmpl_root = os.path.join(os.path.dirname(__file__),
                                      "data",
                                      "web",
                                      "templates")


        self.app = Flask(__name__,
                         template_folder=self.tmpl_root)

        static = Static.File("/tmp")
        static.processors = {
            ".py": script.PythonScript,
            ".rpy": script.ResourceScript
        }
        static.indexNames = ["index.rpy",
                             "index.html",
                             "index.htm"]

        root = Root(self)
        root.putChild("static", static)

        site = WebSocketSite(root)
        site.addHandler("/ws", TestHandler)

        self.service.reactor.listenTCP(self.cfg.get("port", 9002),
                                       site)



        @self.app.route("/")
        def index():
            return render_template("index.html")


    def template(self, path):

        return os.path.join(self.tmpl_root, path)

class Root(Resource):

    def __init__(self, plugin):

        Resource.__init__(self)

        self.wsgi = WSGIResource(plugin.service.reactor,
                                 plugin.service.reactor.getThreadPool(),
                                 plugin.app)


    def getChild(self, child, request):
        request.prepath.pop()
        request.postpath.insert(0, child)
        return self.wsgi


    def render(self, request):
        return self.wsgi.render(request)


class TestHandler(WebSocketHandler):

    def __init__(self, transport):
        WebSocketHandler.__init__(self, transport)

    def __del__(self):
        print 'Deleting handler'

    def send_time(self):
        # send current time as an ISO8601 string
        data = datetime.utcnow().isoformat().encode('utf8')
        self.transport.write(data)

    def frameReceived(self, frame):
        print 'Peer: ', self.transport.getPeer()
        self.transport.write(frame)
