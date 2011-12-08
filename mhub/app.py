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
from plugins.byebyestandby import ByeByeStandbyPlugin
from plugins.echo import EchoPlugin
from plugins.latitude import LatitudePlugin
from plugins.mpd_client import MpdPlugin
from plugins.scheduler import SchedulerPlugin
from plugins.scripting import ScriptingPlugin
from plugins.telnet import TelnetPlugin
from plugins.twitter_client import TwitterPlugin
from plugins.web import WebPlugin
from plugins.xmpp import XmppPlugin


class MHubApp(object):

    """
    Core application container responsible for managing and running of configured plugins.

    :param cfg: Application configuration dictionary
    :type cfg: dict.
    """

    _class_map = {
        "amqp": AmqpPlugin,
        "byebyestandby": ByeByeStandbyPlugin,
        "echo": EchoPlugin,
        "latitude": LatitudePlugin,
        "mpd": MpdPlugin,
        "scheduler": SchedulerPlugin,
        "scripting": ScriptingPlugin,
        "telnet": TelnetPlugin,
        "twitter": TwitterPlugin,
        "web": WebPlugin,
        "xmpp": XmppPlugin
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

        self.service.metadata["plugins"] = dict()

        plugins_cfg = self.cfg.get("plugins")

        for name, plugin_cfg in plugins_cfg.iteritems():
            p_cls_str = plugin_cfg.get("class").lower()
            p_cls = self._class_map.get(p_cls_str)
            p_enabled = plugin_cfg.get("enabled", False)
            self.service.metadata["plugins"][name] = dict(enabled=p_enabled,
                                                          cfg=plugin_cfg)
            if not p_enabled: continue
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


