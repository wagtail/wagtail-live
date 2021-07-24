const DjangoChannelsPublisher = new GenericWebsocketPublisher(baseURL=window.location.host);
DjangoChannelsPublisher.start();