#!/usr/bin/env python

import json
import pprint
import sys

from twisted.internet import reactor, defer
from txZMQ import ZmqEndpoint, ZmqFactory, ZmqPubConnection, ZmqSubConnection

zf = ZmqFactory()
pe = ZmqEndpoint("bind", "tcp://*:9901")
se = ZmqEndpoint("connect", "tcp://10.0.2.40:9901")
pc = ZmqPubConnection(zf, pe)
sc = ZmqSubConnection(zf, se)
sc.subscribe("") # ("scheduler.scheduler001.new_interval")


pc.publish("FUCKING WORK")
sys.exit(0)


def matches(tags, query):

    if query is None: query = list()

    tags = set(tags.split(" "))
    query = set(query)

    return query.issubset(tags)


def on_message(detail, tags):

    print "Tags: %s" % (tags)
    detail = json.loads(detail)

    pc.publish("Testing")
    
    if matches(tags, ["c:owfs"]):
        print "OWFS FTW!"
        pc.publish("HELLO")

    if matches(tags, ["c:tivo", "o:channel"]):
        print detail
        channel = detail.get("channel")
        if channel == 101:
            print "BBC1"

sc.gotMessage = on_message

reactor.run()
