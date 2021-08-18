const baseURL = `${serverHost}:${serverPort}`;
const StarlettePublisher = new GenericWebsocketPublisher(baseURL);
StarlettePublisher.start(); 