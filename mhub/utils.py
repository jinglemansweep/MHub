import ast
import datetime
import optparse
import os
import time
import yaml
from xdg import BaseDirectory


def read_or_generate(filename=None):

    """ Reads configuration (or generates default configuration on first run) """

    base_dir = os.path.join(BaseDirectory.xdg_config_home, "mhub")
    if not os.path.exists(base_dir): os.makedirs(base_dir)

    cache_dir = os.path.join(BaseDirectory.xdg_cache_home, "mhub")
    if not os.path.exists(cache_dir): os.makedirs(cache_dir)

    plugin_cache_dir = os.path.join(cache_dir, "plugins")
    if not os.path.exists(plugin_cache_dir): os.makedirs(plugin_cache_dir)

    if filename is None: filename = os.path.join(base_dir, "config.yml")

    plugins_path = os.path.join(base_dir, "plugins")
    if not os.path.exists(plugins_path): os.makedirs(plugins_path)

    scripts_path = os.path.join(base_dir, "scripts")
    if not os.path.exists(scripts_path): os.makedirs(scripts_path)

    open(os.path.join(scripts_path, "on_init.py"), "a").close()
    open(os.path.join(scripts_path, "on_message.py"), "a").close()
    open(os.path.join(scripts_path, "on_tick.py"), "a").close()

    if os.path.exists(filename):

        stream = file(filename, "r")
        cfg = yaml.load(stream)

    else:

        cfg = {
            "general": {
                "plugins_path": os.path.join(base_dir, "plugins"),
                "cache_path": os.path.join(cache_dir),
                "poll_interval": 0.1
            },
            "amqp": {
                "host": "localhost",
                "port": 5672,
                "username": "guest",
                "password": "guest"
            }
        }

        stream = file(filename, "w")
        yaml.dump(cfg, stream)

    stream.close()

    return cfg






