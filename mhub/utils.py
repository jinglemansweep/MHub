import ast
import datetime
import optparse
import os
import time
import yaml
from xdg import BaseDirectory

from web import generate_app


def server_bootstrap():

    """ Command Line Bootstrap Function """

    parser = generate_option_parser()
    
    (options, args) = parser.parse_args()

    from mhub.controllers import MainController
    controller = MainController(options, args, server=True)
    controller.start()


def client_bootstrap():

    """ Command Line Bootstrap Function """

    parser = generate_option_parser()

    parser.add_option("-a",
                      "--action",
                      dest="action",
                      default="test",
                      help="Action to send [default: %default]")

    parser.add_option("-d",
                      "--data",
                      dest="data",
                      default=None,
                      help="Data to send [default: %default]")

    (options, args) = parser.parse_args()

    if options.data is not None:
        data = ast.literal_eval(options.data)
    else:
        data = dict()

    from mhub.controllers import MainController
    controller = MainController(options, args)

    action = options.action

    controller.send_message({"action": action, "params": data})


def web_bootstrap():

    """ Web interface bootstrap function """

    parser = generate_option_parser()

    (options, args) = parser.parse_args()

    from mhub.controllers import MainController
    controller = MainController(options, args)

    app = generate_app(controller=controller)
    app.run()
    

def configurator(filename=None):

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


def generate_option_parser():

    """ Get command line option parser """

    defaults = get_defaults()
    metadata = defaults.get("metadata")

    usage = metadata.get("usage")
    description = metadata.get("description")
    version = metadata.get("version")

    parser = optparse.OptionParser(usage=usage, description=description, version=version)
    parser = add_default_options(parser)

    return parser

def get_defaults():

    """ Default common configuration """

    defaults = {
        "metadata": {
            "usage": "%prog or type %prog -h (--help) for help",
            "description": "MHub",
            "version": "v0.1"
        }
    }

    return defaults


def add_default_options(parser):

    parser.add_option("-v",
                      action="count",
                      dest="verbosity",
                      default=3,
                      help="Verbosity. Add more -v to be more verbose (%s)")

    parser.add_option("-z",
                      "--logfile",
                      dest="logfile",
                      default=None,
                      help="Log to file instead of console")

    parser.add_option("--host",
                      dest="host",
                      default=None,
                      help="AMQP hostname or address [default: %default]")

    parser.add_option("--port",
                      dest="port",
                      default=None,
                      help="AMQP port [default: %default]")

    return parser


class Timer(object):


    def __init__(self, duration):

        self.duration = duration
        self.start = int(time.time())


    def update(self):

        remaining = ((self.start + self.duration) - int(time.time()))
        elapsed = (self.duration) - remaining

        self.remaining = remaining if remaining > 0 else 0
        self.elapsed = elapsed if elapsed < self.duration else self.duration


    def restart(self):
       
        self.start = int(time.time())
        self.update


    def get_elapsed(self):

        self.update()
        return self.elapsed


    def get_remaining(self):

        self.update()
        return self.remaining


    def is_running(self):

        self.update()
        return (self.remaining >= 0)


    def is_finished(self):

        self.update()
        return (self.remaining < 0)




