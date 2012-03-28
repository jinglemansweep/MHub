#!/usr/bin/env python

import json
import pprint
from twisted.internet import reactor, defer
from txZMQ import ZmqEndpoint, ZmqFactory, ZmqPubConnection, ZmqSubConnection

zf = ZmqFactory()
e = ZmqEndpoint("connect", "tcp://higgs:9901")
s = ZmqSubConnection(zf, e)
s.subscribe("") # ("scheduler.scheduler001.new_interval")

def on_message(*args):

    #json_str = args[0]
    pprint.pprint(args)
    #json_obj = json.loads(json_str)
    #pprint.pprint(json_obj)

s.gotMessage = on_message

reactor.run()
