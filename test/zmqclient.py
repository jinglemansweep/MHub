#!/usr/bin/env python

import json
import pprint
from twisted.internet import reactor, defer
from txZMQ import ZmqEndpoint, ZmqFactory, ZmqPubConnection, ZmqSubConnection

zf = ZmqFactory()
e = ZmqEndpoint("connect", "tcp://*:9001")
s = ZmqSubConnection(zf, e)
s.subscribe("")

def doPrint(*args):
    json_str = args[0]
    json_obj = json.loads(json_str)
    pprint.pprint(json_obj)

s.gotMessage = doPrint

reactor.run()
