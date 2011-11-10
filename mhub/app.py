"""

MHub Applications Module


.. module:: app
   :platform: Unix
   :synopsis: MHub Applications Module

.. moduleauthor:: JingleManSweep <jinglemansweep@gmail.com>

"""

import logging

from twisted.application.service import MultiService, Application
from twisted.internet import reactor

from service import MHubService
from plugins.amqp import AmqpPlugin
from plugins.xmpp import XmppPlugin
from plugins.scheduler import SchedulerPlugin
from plugins.scripting import ScriptingPlugin
from plugins.echo import EchoPlugin
from plugins.mpd_client import MpdPlugin
from plugins.telnet import TelnetPlugin



class MHubApp(object):

    """
    Core application container responsible for managing and running of configured plugins.

    :param cfg: Application configuration dictionary
    :type cfg: dict.
    """

    _class_map = {
        "amqp": AmqpPlugin,
        "xmpp": XmppPlugin,
        "mpd": MpdPlugin,
        "scheduler": SchedulerPlugin,
        "scripting": ScriptingPlugin,
        "echo": EchoPlugin,
        "telnet": TelnetPlugin
    }

    def __init__(self, cfg=None):

        """
        Constructor
        """

        self.cfg = cfg or dict()
        self.logger = logging.getLogger("app")

        self.reactor = reactor
        self.root_service = MultiService()
        self.service = MHubService(self.cfg, self.reactor)
        self.application = Application("mhub")
        self.root_service.setServiceParent(self.application)


    def initialise(self):

        """
        Initialise the application
        """


        self.initialise_plugins()


    def initialise_plugins(self):

        """
        Initialise all configured and enabled plugins
        """

        self.logger.info("Registering plugins")

        plugins_cfg = self.cfg.get("plugins")

        for name, plugin_cfg in plugins_cfg.iteritems():
            p_cls_str = plugin_cfg.get("class")
            p_cls = self._class_map.get(p_cls_str)
            if not plugin_cfg.get("enabled", False): continue
            p_inst = p_cls(name=name,
                           cls=p_cls_str,
                           service=self.service,
                           cfg=plugin_cfg)
            if hasattr(p_inst, "client"):
                p_inst.client.setServiceParent(self.root_service)
            self.service.install_plugin(name, p_inst)
            self.logger.debug("%s.%s registered" % (p_cls_str, name))

    def get_application(self):

        """
        Get the Twisted application object.

        :returns: Application
        """

        return self.application


