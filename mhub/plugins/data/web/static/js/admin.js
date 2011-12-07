
function setup_event_websocket(url) {

    var Socket = window["MozWebSocket"] || window["WebSocket"],
        ws = new Socket("ws://" + url);
 
    ws.onmessage = function(evt) {
        var data = JSON.parse(evt.data), el;
        el = $("<div></div>").text(data.signal);
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
