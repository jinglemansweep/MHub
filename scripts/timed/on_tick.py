
bbs_a1 = state.get("bbs_a1", False)

#send_message("HELLo", key="input.test")

dt = env.get("datetime")
new_minute, new_second = dt.get("new_minute"), dt.get("new_second")

if new_minute: # and dt.get("hour_minute") == "2028":
    #send_message({"action": "byebyestandby", "params": {"device": "a1", "state": not bbs_a1}})
    state["bbs_a1"] = not bbs_a1
