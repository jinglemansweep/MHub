import ast
import datetime
import optparse
import os
import time
import yaml
from xdg import BaseDirectory


def server_bootstrap():

    """ Command Line Bootstrap Function """

    usage = "%prog or type %prog -h (--help) for help"
    description = "MHub"
    version = "v0.1"

    parser = optparse.OptionParser(usage=usage, description=description, version=version)

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
    
    (options, args) = parser.parse_args()

    from mhub.controllers import MainController
    controller = MainController(options, args, server=True)
    controller.start()


def client_bootstrap():

    """ Command Line Bootstrap Function """

    usage = "%prog or type %prog -h (--help) for help"
    description = "MHub"
    version = "v0.1"

    parser = optparse.OptionParser(usage=usage, description=description, version=version)

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

    parser.add_option("-k",
                      "--key",
                      dest="key",
                      default="default",
                      help="Plugin or provider key [default: %default]")

    parser.add_option("--host",
                      dest="host",
                      default=None,
                      help="AMQP hostname or address [default: %default]")

    parser.add_option("--port",
                      dest="port",
                      default=None,
                      help="AMQP port [default: %default]")

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


def configurator(filename=None):

    base_dir = os.path.join(BaseDirectory.xdg_config_home, "mhub")
    if not os.path.exists(base_dir): os.makedirs(base_dir)

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
                "plugins_path": os.path.join(base_dir, "plugins")
            },
            "amqp": {
                "host": "localhost",
                "port": 5672,
                "username": "guest",
                "password": "guest"
            },
            "plugins": {
                "byebyestandby": {
                    "enabled": False,
                    "host": "192.168.1.100",
                    "port": 53008
                },
                "echo": {
                    "enabled": True
                },
                "email": {
                    "enabled": False,
                    "from_address": "user@gmail.com",
                    "smtp_host": "smtp.gmail.com",
                    "smtp_port": 587,
                    "smtp_username": "user@gmail.com",
                    "smtp_password": "ChangeMe",
                    "smtp_start_tls": True
                },
                "logic_processor": {
                    "enabled": False,
                    "scripts_path": os.path.join(base_dir, "scripts"),
                    "scripts": {
                       "on_init": ["on_init.py"],
                        "on_message": ["on_message.py"],
                        "on_tick": ["on_tick.py"]
                    }
                },
                "twitter": {
                    "enabled": False,
                    "consumer_key": "czjLv9TriwG8hZecPRsVA",
                    "consumer_secret_key": "T5XYR3MIWcTVBe4V4ENrWBPeUSwChKz950xvrUoz98",
                    "access_token_key": "ChangeMe",
                    "access_token_secret": "ChangeMe",
                    "timelines": ["BBCNews"],
                    "poll_interval": 300
                },
                "rss": {
                    "enabled": False,
                    "feeds": ["http://feeds.bbci.co.uk/news/rss.xml"],
                    "poll_interval": 300
                },
                "lirc": {
                    "enabled": False,
                    "lircd_socket": "/dev/lircd"
                },
                "websocket": {
                    "enabled": False
                }
            }
        }

        stream = file(filename, "w")
        yaml.dump(cfg, stream)

    stream.close()

    return cfg


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




