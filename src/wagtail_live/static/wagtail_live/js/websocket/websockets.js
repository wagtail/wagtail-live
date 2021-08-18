const baseURL = `${serverHost}:${serverPort}`;
const WebsocketsPublisher = new GenericWebsocketPublisher(baseURL);
WebsocketsPublisher.start(); 