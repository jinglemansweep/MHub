
function setup_event_websocket(url) {

    var Socket = window["MozWebSocket"] || window["WebSocket"],
        ws = new Socket("ws://" + url);
 
    ws.onmessage = function(evt) {
        var data = JSON.parse(evt.data), 
            el, header, signal, name, meta, detail;
        el = $("<div></div>").addClass("event-console-entry");
        header = $("<p></p>").addClass("header");
        signal = $("<span></span>").addClass("signal").text(data.signal);
        sender = $("<span></span>").addClass("sender").text(data.sender);
        header.append(signal).append(sender);
        detail = $("<p></p>").addClass("detail").text(JSON.stringify(data.detail));
        el.append(header).append(detail);
        $("#event-console").prepend(el);
    }
        
    ws.onopen = function(evt) {
        console.log("WS Open");
    }
       
    ws.onerror = function(evt) {
        console.log("WS Error");
    }
       
    ws.onclose = function(evt) {
        console.log("WS Close");
    }

};
