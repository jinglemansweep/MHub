import logging
import louie
import os
import shelve
import sys

from pymongo import Connection


class BasePlugin(object):

    """
    Plugin base class.
    """

    def setup(self, cfg):

        """
        Setup plugin.
        """

        self.cfg = cfg or dict()
        self.cfg["_id"] = "plugin.%s.!config" % (self.name)

        app_cfg = self.service.cfg.get("app")
        cache_dir = app_cfg.get("general").get("cache_dir")
        mongo_server = app_cfg.get("general").get("mongo_server", "localhost")
        mongo_port = app_cfg.get("general").get("mongo_port", 27017)

        plugin_cache_dir = os.path.join(cache_dir, "plugins", self.cls, self.name)

        if not os.path.exists(plugin_cache_dir):
            os.makedirs(plugin_cache_dir)

        self.cache_dir = plugin_cache_dir
        self.state.save(self.cfg)

        louie.connect(self.reconfigure, "app.reconfigure")


    def publish_event(self, event_name, detail=None, send_as=None):

        """
        Publish (send) event to service.

        :param event_name: Name of event.
        :type event_name: str.
        :param detail: Detail dictionary.
        :type detail: dict.
        """

        self.logger.info("Published '%s' event (from '%s.%s')" % (event_name, self.cls, self.name))
        if detail is not None: self.logger.debug(detail)

        kwargs = {
            "signal": event_name,
            "sender": send_as or self.name,
            "cls": self.cls
        }

        if detail is not None:
            kwargs["detail"] = detail

        louie.send(**kwargs)


    def reconfigure(self):

        """
        Retrieves plugins operating configuration

        :param cfg: Configuration object.
        """

        self.logger.debug("Reconfiguring plugin '%s'" % (self.name))
        self.cfg = self.state_get("!config", self.default_config)


    def state_get(self, key, default=None):

        result = self.state.find_one({
            "_id": self.state_key(key),
        })

        if default:
            result["value"] = default
            self.state.save(result)

        if result:
            return result.get("value", default)
        else:
            return default




    def state_save(self, key, value):

        self.state.save({
            "_id": self.state_key(key),
            "value": value
        })

        
    def state_key(self, key):

        """
        Generates fully qualified plugin key

        :param key: Name of key.
        :type key: str.
        """

        return "%s.%s.%s" % ("plugin", self.name, key)
