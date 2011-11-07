import logging


class BasePlugin(object):

    """
    Plugin base class.

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

        self.name = name
        self.cls = cls or "plugin"
        self.service = service
        self.cfg = cfg
        self.logger = logging.getLogger("plugin")
        self.queue = list()


    def process_queue(self):

        """
        Process messages received from service.
        """

        while len(self.queue):
            msg = self.queue.pop()
            self.process_message(msg)


    def process_message(self, msg):

        """
        Message processing callback function.

        :param msg: Message dictionary.
        :type msg: dict.
        """

        pass
    

    def publish_event(self, name, detail):

        """
        Publish (send) event to service.

        :param name: Name of event.
        :type name: str.
        :param detail: Detail dictionary.
        :type detail: dict.
        """

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