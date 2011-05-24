import datetime
import thread

from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler


class Plugin(object):

    """ WebSocket Plugin """

    def __init__(self, cfg, publisher, logger):

        """ Constructor """

        self.cfg = cfg
        self.publisher = publisher
        self.logger = logger
        

    def on_init(self):

        """ Main plugin initialisation """

        self.server = pywsgi.WSGIServer(('127.0.0.1', 8000),
                                        websocket_app,
                                        handler_class=WebSocketHandler)

        self.server.serve_forever()
        #thread.start_new_thread(self.start_server, ())

        
    def on_tick(self):

        """ On tick handler """

        pass
        

    def on_message(self, data, message):

        """ On AMQP message handler """

        action, params = data.get("action"), data.get("params")

        #self.connection.send(data)
        

    def start_server(self):

        """ Start Websocket server """

        self.server.serve_forever()



def websocket_app(environ, start_response):
    if environ["PATH_INFO"] == '/echo':
        ws = environ["wsgi.websocket"]
        message = ws.wait()
        ws.send(message)

