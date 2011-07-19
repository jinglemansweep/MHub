import datetime
import time

from socket import socket, AF_INET, SOCK_DGRAM


class Plugin(object):

    """ ByeByeStandby online controller plugin """

    def __init__(self, cfg, producer, logger):

        """ Constructor """

        self.name = "byebyestandby"
        self.description = "ByeByeStandby home automation integration"
        self.author = "MHub"
        self.cfg = cfg
        self.producer = producer
        self.logger = logger
        self.tasks = list()


    def on_init(self):

        """ Main plugin initialisation """

        self.socket = socket(AF_INET, SOCK_DGRAM)
        

    def on_message(self, data, message):

        """ On AMQP message handler """

        action, params = data.get("action"), data.get("params")

        if action == "%s.action" % (self.name):
            device, state = params.get("device", None), params.get("state", None)
            device = device.upper()
            state_desc = "ON" if state else "OFF"
            if device is not None and state is not None:
                self.logger.info("ByeByeStandby Trigger: %s %s" % (device, state_desc))
                self.switch(device, state)

        if action == "%s.scene" % (self.name):
            scenes = self.cfg.get("scenes", dict())
            name = params.get("name")
            if name in scenes:
                self.logger.debug("Scene '%s' running" % (name))
                scene = scenes.get(name)
                for action in scene:
                    device, state = action.get("device"), action.get("state")
                    self.switch(device, state)

                
    def switch(self, device, state):

        """ BBS device switcher helper """

        state = 1 if state else 0
        h, u = device[0], device[1:]
        cmd = "D:%i%s%02d:E" % (int(state), h.upper(), int(u))
        self.socket.sendto(cmd, (self.cfg.get("host"), self.cfg.get("port")))
        time.sleep(1)
