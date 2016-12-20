from notify import consumers
from channels import route

channel_routing = [
    route('websocket.connect', consumers.ws_connect, path=r"^/messages"),
    route('websocket.receive', consumers.ws_receive, path=r"^/messages"),
    route('websocket.disconnect', consumers.ws_disconnect, path=r"^/messages"),
]
