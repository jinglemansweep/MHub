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

    parser.add_option("-a",
                      "--action",
                      dest="action",
                      default="test",
                      help="Action to send [default: %default]")

    parser.add_option("-p",
                      "--params",
                      dest="params",
                      default=None,
                      help="Params to send [default: %default]")

    (options, args) = parser.parse_args()

    if options.params is not None:
        params = ast.literal_eval(options.params)
    else:
        params = dict()

    from mhub.controllers import MainController
    controller = MainController(options, args)

    routing_key = "input.%s" % (options.key)
    action = options.action

    controller.send_message({"action": action, "params": params}, key=routing_key)


def configurator(filename=None):

    base_dir = os.path.join(BaseDirectory.xdg_config_home, "mhub")
    if not os.path.exists(base_dir): os.makedirs(base_dir)
    if filename is None: filename = os.path.join(base_dir, "config.yml")
    if os.path.exists(filename):
        stream = file(filename, "r")
        cfg = yaml.load(stream)
    else:
        cfg = {
            "amqp": {
                "host": "localhost",
                "port": 5672,
                "username": "guest",
                "password": "guest"
            },
            "plugins": {
                "logic_processor": {
                    "enabled": True,
                    "scripts": {
                       "on_init": ["scripts/event/on_init.py"],
                        "on_message": ["scripts/event/on_message.py"],
                        "on_tick": ["scripts/timed/on_tick.py"]
                    }
                },
                "byebyestandby": {
                    "enabled": True
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




