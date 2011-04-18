if(env.datetime.year == 2011) {
    state["wooooo"] = "12345";
}

if(env.datetime.second > 40) {
    handler.add_action("test_provider", "test_action", {"p1": "test"});
}
