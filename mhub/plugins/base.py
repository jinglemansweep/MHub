import logging
import louie


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


    def publish_event(self, event_name, detail):

        """
        Publish (send) event to service.

        :param event_name: Name of event.
        :type event_name: str.
        :param detail: Detail dictionary.
        :type detail: dict.
        """

        self.logger.info("Published '%s' event (from '%s.%s')" % (event_name, self.cls, self.name))
        self.logger.debug(detail)
    
        louie.send(event_name,
                   self.name,
                   detail, 
                   cls=self.cls) 

