import json
import logging
import os
from twisted.internet import reactor
from twisted.internet.protocol import Protocol, Factory
from twisted.protocols.policies import ProtocolWrapper, WrappingFactory
from twisted.web import static as Static, server, twcgi, script, vhost
from lib.websocket import WebSocketHandler, WebSocketSite
from twisted.web.resource import Resource
from twisted.web.wsgi import WSGIResource
from flask import Flask, g, request, render_template, redirect

from base import BasePlugin



class WebPlugin(BasePlugin):

    """
    Simple Web plugin.
    """

    default_config = {
        "enabled": False,
        "port": 9002
    }


    def setup(self, cfg):

        BasePlugin.setup(self, cfg)

        self.data_root = os.path.join(os.path.dirname(__file__),
                                     "data",
                                     "web")

        self.app = Flask(__name__,
                         template_folder=os.path.join(self.data_root,
                                                      "templates"))

        static = Static.File(os.path.join(self.data_root, "static"))
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
        WebSocketProtocol.plugin = self
        site.addHandler("/ws", WebSocketProtocol)

        self.service.reactor.listenTCP(self.cfg.get("port", 8901),
                                       site)


        @self.app.route("/")
        def index():
            return redirect("/admin/" % (web_prefix))

        @self.app.route("/reconfigure/")
        def reconfigure():
            self.publish_event("app.reconfigure")
            return redirect("/")

        @self.app.route("/admin/")
        def admin():
            ctx = self.context_processor()
            return render_template("admin/home.html", **ctx)

        @self.app.route("/admin/resources/")
        def admin_resources():
            ctx = self.context_processor()
            return render_template("admin/resources.html", **ctx)


    def context_processor(self):

        """ Default template context processor """

        ws_host = self.cfg.get("ws_host", "localhost")
        ws_port = self.cfg.get("ws_port", self.cfg.get("port", 8901))
        ws_path = self.cfg.get("ws_path", "ws")

        ctx = {
            "ws_url": "%s:%s/%s" % (ws_host, ws_port, ws_path)
        }
        

        return ctx


    def template(self, path):

        """ Template location helper """

        return os.path.join(self.data_root, 
                            "templates", 
                            path)


class Root(Resource):

    """ Twisted web root resource """

    def __init__(self, plugin):

        """ Constructor """

        Resource.__init__(self)

        self.wsgi = WSGIResource(plugin.service.reactor,
                                 plugin.service.reactor.getThreadPool(),
                                 plugin.app)


    def getChild(self, child, request):

        """ Get web child resource helper """

        request.prepath.pop()
        request.postpath.insert(0, child)
        return self.wsgi


    def render(self, request):

        """ WSGI renderer helper """

        return self.wsgi.render(request)


class WebSocketProtocol(WebSocketHandler):

    """ WebSocket Protocol """
    
    def __init__(self, transport):

        """ Constructor """

        WebSocketHandler.__init__(self, transport)


    def frameReceived(self, frame):

        """ Message received helper """

        print 'Peer: ', self.transport.getPeer()
        self.transport.write(frame)

    def connectionMade(self):

        """ Connection made helper """

        print 'Connected to client.'
        self.plugin.subscribe(self.process_event)


    def connectionLost(self, reason):

        """ Connection lost helper """

        print 'Lost connection.'

    def process_event(self, signal, detail):

        """ Event publisher helper """

        msg = dict(signal=signal,
                   detail=detail)

        self.transport.write(json.dumps(msg))


class FlashSocketPolicy(Protocol):

    """ Flash socket policy server """
    
    def connectionMade(self):

        """ Connection made helper """

        policy = '<?xml version="1.0"?><!DOCTYPE cross-domain-policy SYSTEM ' \
                 '"http://www.macromedia.com/xml/dtds/cross-domain-policy.dtd">' \
                 '<cross-domain-policy><allow-access-from domain="*" to-ports="*" /></cross-domain-policy>'
        self.transport.write(policy)
        self.transport.loseConnection()

