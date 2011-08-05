import os
import yaml

from socket import gethostname
from xdg import BaseDirectory


def configure():

    """ Read (or create) configuration files and directories """
    
    xdg_config = BaseDirectory.xdg_config_home
    xdg_cache = BaseDirectory.xdg_cache_home

    config_dir = os.path.join(xdg_config, "mhub")
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
        
    cache_dir = os.path.join(xdg_cache, "mhub")
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
        
    plugins_dir = os.path.join(config_dir, "plugins")
    if not os.path.exists(plugins_dir):
        os.makedirs(plugins_dir)

    scripts_dir = os.path.join(config_dir, "scripts")
    if not os.path.exists(scripts_dir):
        os.makedirs(scripts_dir)

    open(os.path.join(scripts_dir, "on_init.py"), "a").close()
    open(os.path.join(scripts_dir, "on_message.py"), "a").close()
    open(os.path.join(scripts_dir, "on_tick.py"), "a").close()

    app_config_filename = os.path.join(config_dir, "app.yml")

    if os.path.exists(app_config_filename):

        stream = file(app_config_filename, "r")
        cfg = yaml.load(stream)

    else:

        cfg = generate_default(config_dir,
                               cache_dir,
                               plugins_dir,
                               scripts_dir)

        stream = file(app_config_filename, "w")
        yaml.dump(cfg, stream)
        
    stream.close()

    return cfg

    
def generate_default(config_dir,
                     cache_dir,
                     plugin_dir,
                     scripts_dir):

    """ Generate default configuration """

    cfg = {
        "general": {
            "name": gethostname(),
            "plugin_dir": plugin_dir,
            "config_dir": config_dir,
            "cache_dir": cache_dir,
            "poll_interval": 0.1
        },
        "amqp": {
            "host": "localhost",
            "port": 5672,
            "username": "guest",
            "password": "guest"
        }
    }

    return cfg
