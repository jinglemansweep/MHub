# Summary

mHub is an AMQP based home automation platform providing high-level flow and state control using JavaScript scripts (courtesy of SpiderMonkey). Additional inputs and outputs can be added using simple AMQP producer/consumer concepts.

# Messaging

All messages are sent and received using AMQP routing keys. This key is basically a ID namespacing the message into basic categories, actions and events. Each message should follow the same structure which should encapsulate all configuration and state for all plugins.

## Routing Keys

* mhub.input.[plugin]
* mhub.output.[plugin]

## Message Structure

The standard message structure is as follows. It allows the specification of a device (some plugins may only require or offer a single device, in this case the string "default" should be used). It also allows for the specication of a particular command as well as a map of parameters to use when actioning the command.

    {"device": "", "cmd": "", "params": {}}

### Examples

MPD:

    {"device": "default", "cmd": "volume_up", "params": {"amount": 5}}

X10:

    {"device": "a8", "cmd": "on"}

