class PieSocketPublisher extends GenericWebsocketPublisher {
    initialize_websocket_connection() {
        this.websocket = new WebSocket(
            `wss://${piesocketEndpoint}${channelID}?api_key=${piesocketApiKey}`
        );
    }
}

const publisher = new PieSocketPublisher();
publisher.start();