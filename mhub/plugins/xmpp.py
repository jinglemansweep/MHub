import pprint
import xmpp


class Plugin(object):

    """ XMPP plugin """

    def __init__(self, cfg, producer, logger):

        """ Constructor """

        self.name = "xmpp"
        self.description = "XMPP/Jabber plugin"
        self.author = "MHub"
        self.cfg = cfg
        self.producer = producer
        self.logger = logger
        self.tasks = list()
        

    def on_message(self, data, message):

        """ On AMQP message handler """

        action, params = data.get("action"), data.get("params")

        if action == "%s.send" % (self.name):

            recipient = params.get("recipient")
            body = params.get("body")

            if recipient is not None and body is not None:

                msg = xmpp.protocol.Message(recipient, body)
                self.client.send(msg)

        
    def on_init(self):

        """ On Init """

        self.tasks = [(0.5, self.process_messages)]
        self.jid = xmpp.JID(self.cfg.get("xmpp_host"))
        self.user = self.jid.getNode()
        self.server = self.jid.getDomain()
        self.client = xmpp.Client(self.server, debug=list())
        
        if not self.client.connect(server=(self.cfg.get("xmpp_server"),
                                           self.cfg.get("xmpp_port", 5222))):
            raise IOError("Cannot connect to server")

        if not self.client.auth(self.cfg.get("xmpp_username"), 
                                self.cfg.get("xmpp_password"),
                                self.cfg.get("xmpp_resource", "mhub")):
            raise IOError("Cannot authorise with server")

        self.client.RegisterDisconnectHandler(self.xmpp_disconnect_callback)

        self.client.RegisterHandler("message", 
                                    self.xmpp_message_callback)

        self.client.RegisterHandler("presence",
                                    self.xmpp_presence_callback)

        self.client.sendInitPresence()
        

    def process_messages(self):

        """ Process incoming XMPP messages """

        self.process_xmpp_stream(self.client)


    def process_xmpp_stream(self, client):

        """ Process XMPP stream for messages and presence changes """

        try:
            client.Process(1)
            if not client.isConnected():
                client.reconnectAndReauth()
        except KeyboardInterrupt: 
            return False
        return True


    def xmpp_disconnect_callback(self):

        """ XMPP disconnection handler callback """

        self.client.reconnectAndReauth()


    def xmpp_message_callback(self, client, msg):

        """ XMPP message handler callback """

        body = msg.getBody()
        sender = msg.getFrom()
        sender_address = "%s@%s" % (sender.getNode(), sender.getDomain())

        if body is None: return

        accepted = any([i in sender_address for i in self.cfg.get("whitelist", list())])
        accepted_str = "accepted" if accepted else "rejected"

        self.logger.debug("XMPP message received from '%s' and was %s" % (sender_address, accepted_str))

        if not accepted: return

        self.producer.publish({
            "action": "%s.input" % (self.name),
            "params": {
                "body": str(body),
                "sender": {
                     "address": sender_address,
                     "domain": sender.getDomain(),
                     "resource": sender.getResource(),
                     "node": sender.getNode()
                }
            }
        })

        if self.cfg.get("acknowledge_messages", False):
            reply = xmpp.protocol.Message(sender, "Acknowledged")
            self.client.send(reply)

            
    def xmpp_presence_callback(self, client, presence):

        """ XMPP presence handler callback """

        sender = presence.getFrom()
        resource = sender.getResource()
        pres_type = presence.getType()
        pres_status = presence.getStatus()

        if pres_type is None: pres_type = "online"

        self.logger.debug("XMPP presence received from '%s'" % sender)

        self.producer.publish({
            "action": "%s.presence" % (self.name),
            "params": {
                "sender": {
                     "domain": sender.getDomain(),
                     "resource": sender.getResource(),
                     "node": sender.getNode()
                },
                "resource": resource,
                "type": pres_type
            }
        })

        if pres_type == "subscribe":
            
            print "Presence subscription from '%s'" % (sender)
            client.send(xmpp.Presence(to=sender, typ="subscribed"))
            client.send(xmpp.Presence(to=sender, typ="subscribe"))

