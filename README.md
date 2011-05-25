# Summary

MHub is an AMQP based messaging event platform primarily targeted for home automation scenarios.

It consists of a server component which simply acts as a plugin execution engine.
A client component is also provided to send AMQP messages to the platform for more adhoc uses.
Both of these components communicate with a compatible AMQP server such as RabbitMQ on a
system created and managed "mhub" exchange.

The main functionality of the platform is contained within the plugins.
Each plugin should simply translate between AMQP messages and real life inputs and outputs.
For example, the RSS feed plugin simply polls RSS feeds at a configured interval and converts any
new articles into AMQP messages. A plugin can also respond to any AMQP messages sent as with the
Twitter plugin which not only polls configured timelines converting new tweets to messages,
but also responds to specific messages and posts updates to Twitter.

See the wiki for more information.