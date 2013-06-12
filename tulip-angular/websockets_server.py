import tulip
import websockets
import logging


logging.basicConfig(level=logging.WARNING)
logging.getLogger('websockets').setLevel(logging.DEBUG)


@tulip.coroutine
def ws_tulip(websocket, uri):
    while True:
        message = yield from websocket.recv()
        websocket.send("ws> {}".format(message))


if __name__ == '__main__':
    websockets.serve(ws_tulip, '127.0.0.1', 8081)
    tulip.get_event_loop().run_forever()
