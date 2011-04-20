//var t = handler.get_timer("test", 10);
state["timer_test"] = core_timer.is_running();

if(env.datetime.year == 2011) {
    state["wooooo"] = "12345";
}

if(env.datetime.second > 40) {
    handler.add_action("test_provider", "test_action", {"p1": "test"});
}

function hello() {
    for(var i=0; i<10; i++) {
        state["hello"+i] = i
    }
}

hello();


