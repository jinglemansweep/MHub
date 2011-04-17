#!/usr/bin/env python2

from mhub.controllers import MainController

controller = MainController({})
controller.send_message({"key": "event.x10", "params": {"device": "a1", "state": "on"}})