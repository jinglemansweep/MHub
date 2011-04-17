import os
import yaml
from xdg import BaseDirectory

def load_configuration(filename=None):

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