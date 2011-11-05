import logging


class BasePlugin(object):

    def __init__(self, name, cls, service, cfg):

        self.name = name
        self.cls = cls or "plugin"
        self.service = service
        self.cfg = cfg
        self.logger = logging.getLogger("plugin")
        self.queue = list()


    def process_queue(self):

        while len(self.queue):
            msg = self.queue.pop()
            self.process_message(msg)


    def process_message(self, msg):

        pass
    

    def publish_event(self, name, detail):

        msg = {
            "type": "event",
            "event": name,
            "source": {
                "class": self.cls,
                "name": self.name
            },
            "detail": detail
        }

        self.logger.info("Published '%s' event (from '%s.%s')" % (name, self.cls, self.name))
        self.logger.debug(detail)

        self.service.queue.append(msg)
        self.service.process_queue()