from twisted.web import xmlrpc


class XMLRPCService(xmlrpc.XMLRPC):

    cs = None

    def xmlrpc_send_message(self, action, params):

        msg = dict(action=action, params=params)

        self.cs.amqp_send_message(msg)
        return "DONE"
