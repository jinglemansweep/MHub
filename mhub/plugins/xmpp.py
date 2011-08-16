import pprint
import xmpp
import sys

from socket import socket, AF_INET, SOCK_DGRAM
from twisted.python import log


class Plugin(object):

    """ XMPP plugin """


    name = "xmpp"
    description = "XMPP/Jabber plugin"
    author = "MHub"

    default_config = {
        "host": "gmail.com",
        "server": "talk.google.com",
        "port": 5223,
        "username": "username",
        "password": "password",
        "resource": "MHub",
        "acknowledge_messages": False,
        "whitelist": []
    }
        

    def on_message(self, data, message):

        """ On AMQP message handler """

        action, params = data.get("action"), data.get("params")

        if action == "%s.send" % (self.name):

            recipient = params.get("recipient")
            body = params.get("body")

            if recipient is not None and body is not None:

                msg = xmpp.Message(to=recipient, 
                                   body=body,
                                   typ="chat")
                self.client.send(msg)

        
    def on_init(self):

        """ On Init """

        self.tasks = [
            (0.5, self.process_messages),
            (10, self.connect)
        ]        
        self.online = False
        
        self.connect()

        

    def connect(self):

        """ Connect and keep alive """

        try:
            test_socket = socket(AF_INET, SOCK_DGRAM)
            test_socket.sendto("", (self.cfg.get("server"), self.cfg.get("port")))
        except:
            self.logger.debug("Network problem")
            self.online = False
        
        if self.online:
            self.client.send(" ")
        else:
            try:
                jid_username = "%s@%s" % (self.cfg.get("username"), self.cfg.get("host"))
                self.jid = xmpp.JID(jid_username)
                self.user = self.jid.getNode()
                self.server = self.jid.getDomain()
                self.client = xmpp.Client(self.server, 
                                          debug=list())
                self.client.connect(server=(self.cfg.get("server"),
                                            self.cfg.get("port", 5222)))
                self.client.auth(self.cfg.get("username"), 
                                 self.cfg.get("password"),
                                 self.cfg.get("resource", "mhub"))
                self.client.RegisterDisconnectHandler(self.xmpp_disconnect_callback)
                self.client.RegisterHandler("message", 
                                            self.xmpp_message_callback)
                self.client.RegisterHandler("presence",
                                            self.xmpp_presence_callback)
                self.client.sendInitPresence()
                self.online = True
                self.logger.debug("Connected to XMPP")
            except Exception, e:
                self.logger.debug("Cannot connect to XMPP")
                self.online = False


    def process_messages(self):

        """ Process incoming XMPP messages """

        if self.online:
            self.process_xmpp_stream(self.client)


    def process_xmpp_stream(self, client):

        """ Process XMPP stream for messages and presence changes """

        if self.online:
            try:
                client.Process(1)
            except xmpp.protocol.SystemShutdown, e:
                self.logger.debug("XMPP server disconnected")
                self.online = False
            except KeyboardInterrupt:
                return False
            except:
                log.msg(sys.exc_info()[0])
            return True


    def xmpp_disconnect_callback(self):

        """ XMPP disconnection handler callback """

        log.msg("XMPP reconnecting")

        self.client.reconnectAndReauth()


    def xmpp_message_callback(self, client, msg):

        """ XMPP message handler callback """

        username = self.cfg.get("username")
        to = str(msg.getTo().getNode())
        body = msg.getBody()
        sender = msg.getFrom()
        sender_address = "%s@%s" % (sender.getNode(), sender.getDomain())
        
        print "username " + username
        print "to " + to
        print "sender " + str(sender)


        if body is None: return

        accepted = any([i in sender_address for i in self.cfg.get("whitelist", list())])
        accepted_str = "accepted" if accepted else "rejected"

        self.logger.debug("XMPP message received from '%s' and was %s" % (sender_address, accepted_str))
        self.logger.debug(body)

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
            
            self.logger.debug("Presence subscription from '%s'" % (sender))
            client.send(xmpp.Presence(to=sender, typ="subscribed"))
            client.send(xmpp.Presence(to=sender, typ="subscribe"))


