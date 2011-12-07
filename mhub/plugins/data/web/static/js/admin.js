
function setup_event_websocket(url) {

    var Socket = window["MozWebSocket"] || window["WebSocket"],
        ws = new Socket("ws://" + url);
 
    ws.onmessage = function(evt) {
        var data = JSON.parse(evt.data), el, header, meta, detail;
        el = $("<div></div>").addClass("event-console-entry");
        header = $("<h2></h2>").text(data.signal);
        meta = $("<p></p>").addClass("meta").text(data.sender);
        detail = $("<p></p>").addClass("detail").text(JSON.stringify(data.detail));
        el.append(header).append(meta).append(detail);
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
