action, params = message.get("action"), message.get("params")

if action == "schedule":

    if params.get("name") == "morning":

        send_message({
            "action": "byebyestandby.action",
            "params": {"device": "A1", "state": False}
        })
    
        send_message({
            "action": "byebyestandby.action",
            "params": {"device": "A2", "state": False}
        })

    elif params.get("name") == "evening":

        send_message({
            "action": "byebyestandby.action",
            "params": {"device": "A1", "state": True}
        })

        send_message({
            "action": "byebyestandby.action",
            "params": {"device": "A2", "state": True}
        })

    elif params.get("name") == "shutdown":

        send_message({
            "action": "byebyestandby.action",
            "params": {"device": "A1", "state": False}
        })

        send_message({
            "action": "byebyestandby.action",
            "params": {"device": "A2", "state": False}
        })

        send_message({
            "action": "byebyestandby.action",
            "params": {"device": "A3", "state": False}
        })

