function get_pos(c, e) {
    var rect = c.getBoundingClientRect();
    return [e.clientX - rect.left, e.clientY - rect.top];
};

function get_modifiers(e) {
    var modifiers = [];
    if (e.altKey) modifiers.push("alt");
    if (e.ctrlKey) modifiers.push("ctrl");
    if (e.metaKey) modifiers.push("meta");
    if (e.shiftKey) modifiers.push("shift");
    return modifiers;
};

function get_key(e) {
    var keynum = null;
    if (window.event) { // IE
        keynum = e.keyCode;
    } else if (e.which) { // Netscape/Firefox/Opera
        keynum = e.which;
    }
    return keynum;
};

function gen_mouse_event(c, e, type) {
    if (c._eventinfo.is_button_pressed)
        var button = e.button;
    else
        button = null;
    var pos = get_pos(c, e);
    var modifiers = get_modifiers(e);
    var press_event = c._eventinfo.press_event;
    var event = {
        "source": "browser",
        "event":
        // Mouse Event
        {
            "name": "MouseEvent",
            "properties": {
                "type": type,
                "pos": pos,
                "button": e.button,
                "is_dragging": press_event != null,
                "modifiers": modifiers,
                "press_event": press_event,
                "delta": null,
            }
        }
    };
    return event;
};

function gen_key_event(c, e, type) {
    var modifiers = get_modifiers(e);
    var key_code = get_key(e);
    var key_text = String.fromCharCode(key_code);
    var event = {
        "source": "browser",
        "event":
        // Key Event
        {
            "name": "KeyEvent",
            "properties": {
                "type": type,
                "key": key_code,
                "text": key_text,
                "modifiers": modifiers,
            }
        }
    };
    return event;
};

function send_timer_event(w) {
    var event = {
        "event":
        // Poll Event
        {
            "name": "PollEvent",
        }
    };
    w.send(event);
};

require(["widgets/js/widget"], function(WidgetManager) {
    var Widget = IPython.DOMWidgetView.extend({
        render: function() {
            this.$canvas = $('<canvas />')
                .attr('id', 'canvas')
                .attr('tabindex', '1')
                .appendTo(this.$el);

            this.c = this.$canvas[0];
            this.c.width = this.model.get("width");
            this.c.height = this.model.get("height");
            this.canvas2d = this.c.getContext('2d');

            this.c._eventinfo = {
                'type': null,
                'pos': null,
                'button': null,
                'is_dragging': null,
                'key': null,
                'modifiers': [],
                'press_event': null,
                'delta': [],
                'is_button_pressed': 0,
                'last_pos': [-1, -1],
            };

            this.c.interval = 50.0;  // Arbitrary for now
            this.c.timer = setInterval(send_timer_event, this.c.interval, this);
        },

        events: {
            'mousemove': 'mouse_move',
            'mousedown': 'mouse_press',
            'mouseup': 'mouse_release',
            'mousewheel': 'mouse_wheel',
            'keydown': 'key_press',
            'keyup': 'key_release',
        },

        mouse_move: function(e) {
            var event = gen_mouse_event(this.c, e, "mouse_move");
            var pos = event.event.properties.pos;
            var last_pos = this.c._eventinfo.last_pos;
            if (pos[0] != last_pos[0] || pos[1] != last_pos[1])
                this.send(event);
            this.c._eventinfo.last_pos = pos;
        },

        mouse_press: function(e) {
            ++this.c._eventinfo.is_button_pressed;
            var event = gen_mouse_event(this.c, e, "mouse_press");
            this.c._eventinfo.press_event = event.event.properties;
            this.send(event);
        },

        mouse_release: function(e) {
            --this.c._eventinfo.is_button_pressed;
            var event = gen_mouse_event(this.c, e, "mouse_release");
            this.c._eventinfo.press_event = null;
            this.send(event);
        },

        mouse_wheel: function(e) {
            var event = gen_mouse_event(this.c, e, "mouse_wheel");
            var delta = [e.originalEvent.wheelDeltaX / 120, e.originalEvent.wheelDeltaY / 120];
            event.event.properties.delta = delta;
            this.send(event);
            // Keep page from scrolling
            e.preventDefault();
        },

        key_press: function(e) {
            var event = gen_key_event(this.c, e, "key_press");
            this.send(event);
        },

        key_release: function(e) {
            var event = gen_key_event(this.c, e, "key_release");
            this.send(event);
        },

        // Update, whenever value attribute of our widget changes
        update: function() {
            if(this.model.get("is_closing") == true)
            {
                clearInterval(this.c.timer);  // Remove existing timer
                return;
            }

            this.c.width = this.model.get("width");
            this.c.height = this.model.get("height");
            var new_int = this.model.get("interval");
            if(this.c.interval != new_int)  // Update the interval
            {
                this.c.interval = new_int;
                clearInterval(this.c.timer);  // Remove existing and set new one
                this.c.timer = setInterval(send_timer_event, this.c.interval, this);
            }
            var img_str = this.model.get("value");
            var img = new Image();
            img.src = "data:image/png;base64," + img_str;
            this.canvas2d.drawImage(img, 0, 0);
        },
    })
    WidgetManager.register_widget_view("Widget", Widget);
});
