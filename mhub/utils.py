import os
import yaml

from socket import gethostname
from xdg import BaseDirectory


def get_configuration():

    """ Read (or create) configuration files and directories """

    xdg_config = BaseDirectory.xdg_config_home
    xdg_cache = BaseDirectory.xdg_cache_home

    config_dir = os.path.join(xdg_config, "mhub")
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    cache_dir = os.path.join(xdg_cache, "mhub")
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    app_config_filename = os.path.join(config_dir, "app.yml")

    if os.path.exists(app_config_filename):
        stream = file(app_config_filename, "r")
        app_cfg = yaml.load(stream)
    else:
        app_cfg = generate_default(config_dir,
                               cache_dir)
        stream = file(app_config_filename, "w")
        yaml.dump(app_cfg, stream)
    stream.close()

    plugins_config_filename = os.path.join(config_dir, "plugins.yml")

    if os.path.exists(plugins_config_filename):
        stream = file(plugins_config_filename, "r")
        plugins_cfg = yaml.load(stream)
    else:
        plugins_cfg = dict()
        stream = file(plugins_config_filename, "w")
        yaml.dump(plugins_cfg, stream)
    stream.close()

    app_cfg["general"]["app_id"] = "mhub"
    cfg = dict(app=app_cfg, plugins=plugins_cfg)

    return cfg


def generate_default(config_dir,
                     cache_dir):

    """ Generate default configuration """

    cfg = {
        "general": {
            "name": gethostname(),
            "config_dir": config_dir,
            "cache_dir": cache_dir,
            "verbose": False,
        },
        "amqp": {
            "host": "localhost",
            "port": 5672,
            "username": "guest",
            "password": "guest",
            "vhost": "/"
        },
    }

    return cfg