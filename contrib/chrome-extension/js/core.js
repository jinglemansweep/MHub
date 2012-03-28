
// Namespace

var mhub = {};

// Setup

mhub.setup = {

    init: function () {

        this.setupConfiguration();

    },

    setupConfiguration: function () {

        var cfg_pub_key = localStorage["pubnub.pub_key"];
            cfg_sub_key = localStorage["pubnub.sub_key"];
            cfg_channel = localStorage["pubnub.channel"];

        if(typeof cfg_pub_key === "undefined") {
            localStorage["pubnub.pub_key"] = "pub-xxx";
        }

        if(typeof cfg_sub_key === "undefined") {
            localStorage["pubnub.sub_key"] = "sub-xxx";
        }

        if(typeof cfg_channel === "undefined") {
            localStorage["pubnub.channel"] = "mhub";
        }


    }

}; 

// Background Page

mhub.background = {

    init: function () {

        this.setupPubnub();

    },

    setupPubnub: function () {
 
        var pub_key = localStorage["pubnub.pub_key"],
            sub_key = localStorage["pubnub.sub_key"],
            channel = localStorage["pubnub.channel"],
            config, pubnub;

        config = {
            "publish_key": pub_key,
            "subscribe_key": sub_key,
            "ssl": false
        };

        pubnub = PUBNUB.init(config);
        pubnub.ready();

        pubnub.subscribe({
            channel: channel,
            restore: false,
            callback: this.onMessage,
            disconnect: function() {
                mhub.utils.createNotification("Connection lost");
            },
            reconnect: function() {
                mhub.utils.createNotification("And we're back!")
            },
            connect: function() {
                mhub.utils.createNotification("Connected");
            }
        })

    },

    onMessage: function (message) {

        var detail = message.detail,
            tags = message.tags,
            title, body, icon;

        for(i in tags) {
            tag = tags[i].toLowerCase();
            tag_cls = tag.substring(0, 2);
            tag_value = tag.substring(2);
            if(tag_cls === "c:") { msg_cls = tag_value; }
            if(tag_cls === "h:") { msg_host = tag_value; }
            if(tag_cls === "n:") { msg_name = tag_value; }
            //if(tag_cls === "d:") { msg_datetime = tag_value; }
        } 

        msg_datetime = "";

        msg_map = {"class": msg_cls, "host": msg_host, "name": msg_name, "datetime": msg_datetime};

        if(typeof mhub.background.formatters[msg_cls] !== "undefined") {
            rendered = mhub.background.formatters[msg_cls](msg_map, detail);
        } else {
            rendered = {"title": msg_cls.toUpperCase()};
            body = "<dl>";
            for(k in detail) {
                body += "<dt>" + k + ":</dt><dd>" + detail[k] + "</dd>";
            }
            body += "</dl>";
            rendered.body = body;
        }

        icon = "icons/" + msg_cls.toLowerCase() + ".png";

        mhub.utils.createNotification(rendered.body, null, rendered.title, icon);

    },

    formatters: {

        cctv: function (summary, detail) {

            var title, body;
            title = summary["class"].toUpperCase();
            body = "<dl><dt>Level</dt><dd>" + detail.level + "</dd></dl>";
            return {"title": title, "body": body};

        },

        owfs: function (summary, detail) {

            var title, body;
            title = summary["class"].toUpperCase() + ": " + summary["name"];
            body = "<dl>";

            for(k in detail) {
                body += "<dt>" + k + "</dt>";
                body += "<dd>" + detail[k] + "</dd>";
            }

            body += "</dl>";

            return {"title": title, "body": body};
            
        }

    }

};

// Options Page

mhub.options = {

    init: function () {

        this.setupEvents();
        this.loadConfiguration();

    },

    setupEvents: function () {

        $("input#save").bind("click", function (evt) {

            var errors = [],
                form_pub_key = $("input#pub_key").val(),
                form_sub_key = $("input#sub_key").val(),
                form_channel = $("input#channel").val();

            // Validation

            if(form_pub_key === "") { 
                errors.push("No publish key specified");
            }

            if(form_sub_key === "") {
                errors.push("No subscribe key specified");
            } 

            if(form_channel === "") {
                errors.push("No channel specified");
            }
            
            if(errors.length) {
                error_msg = "Cannot save settings:\n\n";
                for(i in errors) {
                    error_msg += "- " + errors[i];
                    if (i < errors.length) { error_msg += "\n"; }
                }
                mhub.utils.createNotification(error_msg);
                return null;
            }
            
            // Saving
            
            localStorage["pubnub.pub_key"] = form_pub_key;
            localStorage["pubnub.sub_key"] = form_sub_key;
            localStorage["pubnub.channel"] = form_channel;

            // Done
            
            alert("Settings saved");

        });

    },

    loadConfiguration: function () {

        var cfg_pub_key = localStorage["pubnub.pub_key"] || "pub-xxx",
            cfg_sub_key = localStorage["pubnub.sub_key"] || "sub-xxx",
            cfg_channel = localStorage["pubnub.channel"] || "mhub";

        $("input#pub_key").val(cfg_pub_key);
        $("input#sub_key").val(cfg_sub_key);
        $("input#channel").val(cfg_channel);

    }

};

// Notification

mhub.notification = {

    init: function () {

        var params = mhub.utils.getQueryParams(),
            container;

        container = $("<div/>").addClass("container");
        title = $("<h1/>").addClass("title").text(params.title);
        content = $("<div/>").addClass("content");
        icon = $("<img/>").addClass("icon").attr({"src": params.icon});
        body = $("<div/>").addClass("body").html(params.body);
        content.append(icon);
        content.append(body);
        container.append(title).append(content);
         
        $("#notification").html(container);

    }

};

// Popup

mhub.popup = {

    init: function () {

    }

};

// Utils

mhub.utils = {

    createNotification: function (body, timeout, title, icon) {

        timeout = (typeof timeout === "undefined" || timeout == null ? 10 : timeout)
        title = (typeof title === "undefined" || title == null ? "MHub" : title);
        icon = (typeof icon === "undefined" || icon == null ? "icon.png" : icon);

        url = "notification.html";
        url += "?title=" + escape(title);
        url += "&body=" + escape(body);
        url += "&icon=" + escape(icon);

        var notification = webkitNotifications.createHTMLNotification(url);
        notification.show();

        setTimeout(function() { notification.cancel(); }, (timeout * 1000));

    },

    getQueryParams: function () {

        var query = window.location.search.substring(1),
            params = {}, regex, match;

        if(query) {
            regex = /(.+?)=(.+?)(?:&|;|$)/g;
            while (match = regex.exec(query)) {
               params[match[1]] = decodeURIComponent(match[2]);
            }
        }

        return params;

    }


}

// Bootstrap

mhub.bootstrap = {
 
    main: function () {
 
        mhub.setup.init();

        if($("body").hasClass("background")) {
            mhub.background.init();
        }
 
        if($("body").hasClass("options")) {
            mhub.options.init();
        }
 
        if($("body").hasClass("popup")) {
            mhub.popup.init();
        }

        if($("body").hasClass("notification")) {
            mhub.notification.init();
        }
 
    }

}


// JQuery

$(document).ready(function () {
    mhub.bootstrap.main();
});
