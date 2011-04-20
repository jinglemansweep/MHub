import datetime
import os
import time
import yaml
from xdg import BaseDirectory


def configurator(filename=None):

    base_dir = os.path.join(BaseDirectory.xdg_config_home, "mhub")
    if not os.path.exists(base_dir): os.makedirs(base_dir)
    if filename is None: filename = os.path.join(base_dir, "config.yml")
    if os.path.exists(filename):
        stream = file(filename, "r")
        cfg = yaml.load(stream)
    else:
        cfg = {
            "scripts": {
                "on_message": ["scripts/message.js"],
                "on_tick": ["scripts/tick.js"]
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

        self.remaining = ((self.start + self.duration) - int(time.time()))
        self.elapsed = (self.duration) - self.remaining


    def reset(self):
       
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


class JSBridge(object):
    

    def __init__(self):
    
        self.actions = list()
        self.timers = dict()


    def add_action(self, provider, action, params=None):

        if params is None: params = dict()

        self.actions.append({"provider": provider, "action": action, "params": params})


    def del_timer(self, name):

        if name in self.timers:
            del self.timers[name]


    def get_timer(self, name, duration):

        if name not in self.timers:
            timer = Timer(duration)
            self.timers[name] = timer
        
        return self.timers.get(name)

