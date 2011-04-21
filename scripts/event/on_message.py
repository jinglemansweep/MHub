
def run(state, env, message=None):

    print "MSG"

    if message is not None:

        key = message.delivery_info.get("routing_key")
        body = message.body

        print "Message received from: %s" % (key)
        print "Message body:\n%s" % (body)

    state["on_message"] = True

    return state
