import logging
import os
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

        self.subscribe(self.reconfigure, "app.reconfigure")


    def subscribe(self, func, pattern=None):

        """
        Create a subscription to an event

        :param func: Callback function.
        :type func: function.
        :param signal: Event signal.
        :param sender: Event sender.
        """

        self.service.subscribe(func, pattern)


    def publish(self, signal, detail=None):

        """
        Publish (send) event to service.

        :param signal: Name of signal.
        :type signal: str.
        :param sender: Name of sender.
        :type signal: str
        :param detail: Detail dictionary.
        :type detail: dict.
        """

        self.service.publish(signal, detail, self)


    def reconfigure(self):

        """
        Retrieves plugins operating configuration

        :param cfg: Configuration object.
        """

        self.logger.debug("Reconfiguring plugin '%s'" % (self.name))
        self.cfg = self.db_get(self.state, "!config", self.default_config)


    def db_get(self, coll, key, default=None):

        result = coll.find_one({
            "_id": self.db_key(key),
        })

        if default:
            result["value"] = default
            coll.save(result)

        if result:
            return result.get("value", default)
        else:
            return default


    def db_save(self, coll, key, value):

        coll.save({
            "_id": self.db_key(key),
            "value": value
        })


    def db_remove(self, coll, key):

        coll.remove({"_id": self.db_key(key)})


    def get_resource(self, key):

        return self.store.find_one({"type": "resource", "_id": "resource.%s" % (key)})


    def get_resources(self, cls):

        return list(self.store.find({"type": "resource", "class": cls}))

        
    def db_key(self, key):

        """
        Generates fully qualified plugin key

        :param key: Name of key.
        :type key: str.
        """

        return "%s.%s.%s" % ("plugin", self.name, key)
