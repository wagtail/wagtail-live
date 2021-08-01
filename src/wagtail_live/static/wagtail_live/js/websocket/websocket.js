class WebsocketPublisher {
    /**
     * Initializes and pens a new websocket connection with server side 
     * or a real-time message service.
     * @constructor
     * @param {String} baseURL - baseURL to use for websocket connections.
     */
    constructor(baseURL) {
        this.baseURL = baseURL;
        this.initialize_websocket_connection();
    }

    /**
     * Registers callbacks on websockets events.
     */
    start() {
        this.initialize_on_message_event();
        this.initialize_on_error_event();
    }

    /**
     * Opens a websocket connection with the baseURL provided.
     */
    initialize_websocket_connection() {}

    /**
     * Registers callback on new message events.
     */
    initialize_on_message_event() {}

    /**
     * Registers callback on disconnect/error events.
     */
    initialize_on_error_event() {}

}

class GenericWebsocketPublisher extends WebsocketPublisher {
    initialize_websocket_connection() {
        this.websocket = new WebSocket(
            `ws://${this.baseURL}/ws/channel/${channelID}/`
        );
    }

    initialize_on_message_event() {
        this.websocket.onmessage = function (e) {
            process_updates(JSON.parse(e.data))
        };
    }

    initialize_on_error_event() {
        this.websocket.onclose = function(e) {
            console.error('Websocket closed unexpectedly.');
        };
    }
}
