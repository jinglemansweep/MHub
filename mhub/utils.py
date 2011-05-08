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

    parser.add_option("-d",
                      "--device",
                      dest="device",
                      default="default",
                      help="Device to target [default: %default]")

    parser.add_option("-c",
                      "--command",
                      dest="command",
                      default="default",
                      help="Command to send [default: %default]")

    (options, args) = parser.parse_args()

    from mhub.controllers import MainController
    controller = MainController(options, args)

    routing_key = "input.%s" % (options.key)
    device = options.device
    command = options.command

    controller.send_message({"device": device, "cmd": command}, key=routing_key)


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
            "helpers": {
                "email": {
                    "smtp": {
                        "default": {
                            "from": "user@gmail.com",
                            "host": "smtp.gmail.com",
                            "port": 587,
                            "username": "user@gmail.com",
                            "password": "password",
                            "start_tls": True
                        }
                    }
                }
            },
            "scripts": {
                "on_init": ["scripts/event/on_init.py"],
                "on_message": ["scripts/event/on_message.py"],
                "on_tick": ["scripts/timed/on_tick.py"]
            }
        }
        stream = file(filename, "w")
        yaml.dump(cfg, stream)
    stream.close()
    return cfg


def find_plugins(path, cls):

    """
    Find all subclass of cls in py files located below path
    (does look in sub directories)

    @param path: the path to the top level folder to walk
    @type path: str
    @param cls: the base class that all subclasses should inherit from
    @type cls: class
    @rtype: list
    @return: a list if classes that are subclasses of cls
    """

    subclasses=[]

    def look_for_subclass(modulename):
        #log.debug("searching %s" % (modulename))
        module=__import__(modulename)

        #walk the dictionaries to get to the last one
        d=module.__dict__
        for m in modulename.split('.')[1:]:
            d=d[m].__dict__

        #look through this dictionary for things
        #that are subclass of Job
        #but are not Job itself
        for key, entry in d.items():
            if key == cls.__name__:
                continue

            try:
                if issubclass(entry, cls):
                    log.debug("Found subclass: "+key)
                    subclasses.append(entry)
            except TypeError:
                #this happens when a non-type is passed in to issubclass. We
                #don't care as it can't be a subclass of Job if it isn't a
                #type
                continue

    for root, dirs, files in os.walk(path):
        for name in files:
            if name.endswith(".py") and not name.startswith("__"):
                path = os.path.join(root, name)
                modulename = path.rsplit('.', 1)[0].replace('/', '.')
                look_for_subclass(modulename)

    return subclasses






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




