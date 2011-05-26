import socket


class Plugin(object):

    """ Schedule Plugin """

    def __init__(self, cfg, producer, logger):

        """ Constructor """

        self.cfg = cfg
        self.producer = producer
        self.logger = logger
        

    def on_init(self):

        """ Main plugin initialisation """

        self.tasks = [(0.10, self.process_events)]
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.setblocking(False)
        try:
            self.socket.connect(self.cfg.get("lircd_socket", "/dev/lircd"))
        except:
            pass

        
    def process_events(self):

        try:
            data = self.socket.recv(1024)
            self.logger.debug(data)
        except:
            pass