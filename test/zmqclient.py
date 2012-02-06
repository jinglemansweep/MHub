#!/usr/bin/env python

import json
import pprint
from twisted.internet import reactor, defer
from txZMQ import ZmqEndpoint, ZmqFactory, ZmqPubConnection, ZmqSubConnection

zf = ZmqFactory()
e = ZmqEndpoint("connect", "tcp://*:9901")
s = ZmqSubConnection(zf, e)
s.subscribe("") # ("scheduler.scheduler001.new_interval")

def doPrint(*args):
    #json_str = args[0]
    pprint.pprint(args)
    #json_obj = json.loads(json_str)
    #pprint.pprint(json_obj)

s.gotMessage = doPrint

reactor.run()
