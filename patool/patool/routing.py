from channels import route

from notify import consumers

channel_routing = [
    route('websocket.connect', consumers.ws_connect, path=r"^/messages"),
    route('websocket.receive', consumers.ws_receive, path=r"^/messages"),
    route('websocket.disconnect', consumers.ws_disconnect, path=r"^/messages"),
]
