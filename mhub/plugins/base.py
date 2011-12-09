import logging
import louie
import os
import shelve
import sys


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

        self.setup()


    def setup(self):

        """
        Setup plugin.
        """

        cache_dir = self.service.cfg.get("app").get("general").get("cache_dir")

        plugin_cache_dir = os.path.join(cache_dir, "plugins", self.cls, self.name)

        if not os.path.exists(plugin_cache_dir):
            os.makedirs(plugin_cache_dir)

        self.cache_dir = plugin_cache_dir
        self._datastore_filename = os.path.join(self.cache_dir, "storage.shelve")


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


    def store_put(self, key, value):

        """
        Persist a value in the datastore.

        :param key: Name of key.
        :type key: str.
        :param value: Value to store.
        """

        full_key = self._store_key(key)

        ds = shelve.open(self._datastore_filename)
        ds[full_key] = value
        ds.close()


    def store_get(self, key, default=None):

        """
        Retrieve a value from the datastore
        
        :param key: Name of key.
        :type key: str.
        :param default: Default value.
        """

        full_key = self._store_key(key)
        ds = shelve.open(self._datastore_filename)
        if ds.has_key(full_key):
            return ds[full_key]
        else:
            return default
        ds.close()


    def store_del(self, key):

        """
        Remove a value from the datastore
        
        :param key: Name of key.
        :type key: str.
        """

        full_key = self._store_key(key)
        ds = shelve.open(self._datastore_filename)
        if ds.has_key(full_key):
            del ds[full_key]
        ds.close()


    def _store_key(self, key):

        """
        Generates fully qualified plugin key

        :param key: Name of key.
        :type key: str.
        """

        return "%s" % (key)
