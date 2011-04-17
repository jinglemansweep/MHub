#!/usr/bin/env python2

from mhub.controllers import MainController
from mhub.providers import SqueezeboxServerProvider

cfg = {
    "callbacks": {
        "on_message": ["scripts/message.js"]
    }
}

controller = MainController(cfg)

controller.start()