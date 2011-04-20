#!/usr/bin/env python2

from mhub.controllers import MainController

controller = MainController({})
controller.send_message({"key": "input.x10", "device": "a1", "cmd": "on"})
