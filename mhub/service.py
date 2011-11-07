"""

MHub Services Module

.. module:: service
   :platform: Unix
   :synopsis: MHub Services Module

.. moduleauthor:: JingleManSweep <jinglemansweep@gmail.com>

"""

import json
import logging
from twisted.application.service import Service
from twisted.internet import reactor, threads



class BaseService(Service):


    """
    Core service which manages all plugins, factories and protocols and any communications between them.

    :param cfg: Service configuration object
    :type cfg: dict.
    :param reactor: Twisted Reactor object
    :type reactor: twisted.internet.reactor
    """


    def __init__(self,
                 cfg=None,
                 reactor=None):

        """ Constructor """

        cfg = cfg or dict()
        self.reactor = reactor
        self.logger = logging.getLogger("mhub.service")
        self.cfg = cfg
        self.factories = dict()
        self.plugins = dict()
        self.queue = list()


    def setup(self):

        """
        Setup service.
        """

        #self.setup_plugins()
        #self.init_plugins()
        self.setup_reactor()
        

    # Reactor handling

    def setup_reactor(self):

        """
        Setup Twisted reactor.
        """

        print "setup reactor"

        for plugin_name, plugin_inst in self.plugins.iteritems():
            if not hasattr(plugin_inst, "tasks"): continue
            plugin_tasks = plugin_inst.tasks
            print plugin_tasks
            for plugin_task in plugin_tasks:
                interval = plugin_task[0]
                print plugin_task
                func = plugin_task[1]
                self.logger.debug("Registered '%s' from '%s' every %.2f seconds" % (func.__name__,
                                                                          plugin_name,
                                                                          interval))
                def blocking_call(func, interval):
                    d = threads.deferToThread(func)
                    reactor.callLater(interval, blocking_call, func, interval)
                    return d

                d = blocking_call(func, interval)

            self.logger.info("%i tasks declared" % (len(plugin_tasks)))


    def install_plugin(self, name, plugin):

        """
        Install plugin into service.
        """

        self.plugins[name] = plugin
        
    # Proxies for Factories and Protocols



    def process_queue(self):

        """
        Process the incoming service message queue and forward onto all plugins (excluding sending plugin).
        """

        while len(self.queue):
            msg = self.queue.pop()
            for name, plugin in self.plugins.iteritems():
                if plugin.name == msg.get("source").get("name"): continue
                plugin.queue.append(msg)
                plugin.process_queue()

    # Twisted overrides


    def startService(self):
        
        """
        Start the main Twisted service handler.
        """

        self.setup()
        service.Service.startService(self)
        self.logger.info("Service started")


class MHubService(BaseService):

    """ MHub Twisted Service """

    pass


