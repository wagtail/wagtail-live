import asyncio
import json

from starlette.applications import Starlette
from starlette.endpoints import WebSocketEndpoint
from starlette.middleware.cors import CORSMiddleware

from ..redis import RedisBus, make_channel_group_name
from ..utils import get_redis_url


# Define the broadcast method to be used by the bus.
async def broadcast(message, connections):
    message = json.loads(message)
    await asyncio.wait([ws.send_json(message) for ws in connections])


BUS = RedisBus(url=get_redis_url(), broadcast=broadcast)


app = Starlette()

# TODO: Forgot why I did this.
app.add_middleware(CORSMiddleware, allow_origins=["*"])


@app.on_event("startup")
def startup():
    # Run the bus on startup
    asyncio.create_task(BUS.run())


@app.websocket_route("/ws/channel/{channel_id:str}/")
class StarlettePublisherApp(WebSocketEndpoint):
    encoding = "json"

    async def on_connect(self, websocket, **kwargs):
        """Adds this connection to the channel group corresponding to channel_id."""

        await websocket.accept()

        channel_id = websocket.path_params["channel_id"]
        self.channel_group_name = make_channel_group_name(channel_id)
        await BUS.subscribe(self.channel_group_name, websocket)

    async def on_disconnect(self, websocket, close_code):
        """Removes this connection from its channel group."""

        await BUS.unsubscribe(self.channel_group_name, websocket)
