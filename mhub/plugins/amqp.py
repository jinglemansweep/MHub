###
# amqp.py
# AMQPFactory based on txamqp.
#
# Dan Siemon <dan@coverfire.com>
# March 2010
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
##
from twisted.internet import reactor, defer, protocol
from twisted.internet.defer import inlineCallbacks, Deferred
from twisted.application.internet import TCPServer, TCPClient
from txamqp.protocol import AMQClient
from txamqp.client import TwistedDelegate
from txamqp.content import Content
import logging
import txamqp
import os
import json

from base import BasePlugin


class AmqpPlugin(BasePlugin):

    def __init__(self, name, cls, service, cfg):

        BasePlugin.__init__(self, name, cls, service, cfg)

        self.factory = AmqpFactory(plugin=self)
        self.factory.read("*", self.amqp_receive)
        self.client = TCPClient(self.cfg.get("host", "localhost"),
                                         self.cfg.get("port", 5672),
                                         self.factory)

    def amqp_send(self, msg):

        json_msg = json.dumps(msg)
        self.factory.send_message(msg=json_msg)


    def amqp_receive(self, msg):

        self.publish_event("receive", msg)


    def process_message(self, msg):
        
        #self.logger.debug("AMQP: %s" % (msg))
        pass




class AmqpProtocol(AMQClient):
    """The protocol is created and destroyed each time a connection is created and lost."""

    def connectionMade(self):
	"""Called when a connection has been made."""

        AMQClient.connectionMade(self)

        # Flag that this protocol is not connected yet.
        self.connected = False

        # Authenticate.
        deferred = self.start({"LOGIN": self.factory.user, "PASSWORD": self.factory.password})
        deferred.addCallback(self._authenticated)
        deferred.addErrback(self._authentication_failed)


    def _authenticated(self, ignore):

        """Called when the connection has been authenticated."""



        # Get a channel.
        d = self.channel(1)
        d.addCallback(self._got_channel)
        d.addErrback(self._got_channel_failed)


    def _got_channel(self, chan):

        self.chan = chan

        d = self.chan.channel_open()
        d.addCallback(self._channel_open)
        d.addErrback(self._channel_open_failed)


    def _channel_open(self, arg):
        """Called when the channel is open."""

        # Flag that the connection is open.
        self.connected = True

        # Now that the channel is open add any readers the user has specified.
        for l in self.factory.read_list:
            self.setup_read(l[0], l[1], l[2])

        # Send any messages waiting to be sent.
        self.send()

        # Fire the factory's 'initial connect' deferred if it hasn't already
        if not self.factory.initial_deferred_fired:
            self.factory.deferred.callback(self)
            self.factory.initial_deferred_fired = True


    def read(self, exchange, routing_key, callback):
        """Add an exchange to the list of exchanges to read from."""
        if self.connected:
            # Connection is already up. Add the reader.
            self.setup_read(exchange, routing_key, callback)
        else:
            # Connection is not up. _channel_open will add the reader when the
            # connection is up.
            pass

    # Send all messages that are queued in the factory.
    def send(self):
        """If connected, send all waiting messages."""
        if self.connected:
            while len(self.factory.queued_messages) > 0:
                m = self.factory.queued_messages.pop(0)
                self._send_message(m[0], m[1], m[2])


    # Do all the work that configures a listener.
    @inlineCallbacks
    def setup_read(self, exchange, routing_key, callback):
        """This function does the work to read from an exchange."""
        queue = exchange # For now use the exchange name as the queue name.
        consumer_tag = exchange # Use the exchange name for the consumer tag for now.

        # Declare the exchange in case it doesn't exist.
        yield self.chan.exchange_declare(exchange=exchange, type="fanout", durable=True, auto_delete=False)

        # Declare the queue and bind to it.
        yield self.chan.queue_declare(queue=queue, durable=True, exclusive=False, auto_delete=False)
        yield self.chan.queue_bind(queue=queue, exchange=exchange, routing_key=routing_key)

        # Consume.
        yield self.chan.basic_consume(queue=queue, no_ack=True, consumer_tag=consumer_tag)
        queue = yield self.queue(consumer_tag)

        # Now setup the readers.
        d = queue.get()
        d.addCallback(self._read_item, queue, callback)
        d.addErrback(self._read_item_err)




    def _channel_open_failed(self, error):
        print "Channel open failed:", error


    def _got_channel_failed(self, error):
        print "Error getting channel:", error


    def _authentication_failed(self, error):
        print "AMQP authentication failed:", error


    @inlineCallbacks
    def _send_message(self, exchange, routing_key, msg):
        """Send a single message."""
        # First declare the exchange just in case it doesn't exist.
        yield self.chan.exchange_declare(exchange=exchange, type="fanout", durable=True, auto_delete=False)

        msg = Content(msg)
        msg["delivery mode"] = 2 # 2 = persistent delivery.
        d = self.chan.basic_publish(exchange=exchange, routing_key=routing_key, content=msg)
        d.addErrback(self._send_message_err)


    def _send_message_err(self, error):
        print "Sending message failed", error


    def _read_item(self, item, queue, callback):
        """Callback function which is called when an item is read."""
        # Setup another read of this queue.
        d = queue.get()
        d.addCallback(self._read_item, queue, callback)
        d.addErrback(self._read_item_err)

        # Process the read item by running the callback.
        callback(item)

    def _read_item_err(self, error):
        print "Error reading item: ", error




class AmqpFactory(protocol.ReconnectingClientFactory):

    protocol = AmqpProtocol

    def __init__(self, plugin):

        self.plugin = plugin
        self.service = self.plugin.service
        self.service.amqp_factory = self
        app_cfg = self.service.cfg.get("app")
        general_cfg = app_cfg.get("general", dict())
        amqp_cfg = app_cfg.get("amqp", dict())
        spec_file = amqp_cfg.get("spec_file", "%s/rabbitmq.xml" % (os.path.dirname(__file__)))
        self.spec = txamqp.spec.load(spec_file)
        self.user = amqp_cfg.get("user", "guest")
        self.password = amqp_cfg.get("password", "guest")
        self.vhost = amqp_cfg.get("vhost", "/")
        self.host = amqp_cfg.get("host", "localhost")
        self.port = amqp_cfg.get("port", 5672)
        self.exchange = general_cfg.get("app_id")
        self.delegate = TwistedDelegate()
        self.deferred = Deferred()
        self.initial_deferred_fired = False
        self.logger = logging.getLogger("factory")

        self.p = None # The protocol instance.
        self.client = None # Alias for protocol instance

        self.queued_messages = [] # List of messages waiting to be sent.
        self.read_list = [] # List of queues to listen on.

        # Make the TCP connection.
        #reactor.connectTCP(self.host, self.port, self)


    def buildProtocol(self, addr):
        p = self.protocol(self.delegate, self.vhost, self.spec)
        p.factory = self # Tell the protocol about this factory.

        self.p = p # Store the protocol.
        self.client = p

        # Reset the reconnection delay since we're connected now.
        self.resetDelay()

        return p


    def clientConnectionFailed(self, connector, reason):

        self.logger.debug("AMQP failed")
        #print "Connection failed."
        protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)


    def clientConnectionLost(self, connector, reason):
        self.logger.debug("AMQP disconnected")
        self.p = None

        protocol.ReconnectingClientFactory.clientConnectionLost(self, connector, reason)


    def send_message(self, routing_key="", msg=None):
        """Send a message."""
        # Add the new message to the queue.

        self.queued_messages.append((self.exchange, routing_key, msg))

        # This tells the protocol to send all queued messages.
        if self.p != None:
            self.p.send()


    def read(self, routing_key="", callback=None):
        """Configure an exchange to be read from."""
        assert(routing_key != None and callback != None)

        # Add this to the read list so that we have it to re-add if we lose the connection.
        self.read_list.append((self.exchange, routing_key, callback))

        # Tell the protocol to read this if it is already connected.
        if self.p != None:
            self.p.read(self.exchange, routing_key, callback)

