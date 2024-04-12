import json
import numpy
import os
import sys
import threading
import time
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web

n_puzzle_ws_server = None
run = True

class PlannerWSClient():
    def __init__(self, message, ws_server):
        self.message = message
        self.ws_server = ws_server
        self.ws_client = None
        self.connect()
    
    @tornado.gen.coroutine
    def connect(self):
        self.ws_client = yield tornado.websocket.websocket_connect(
            "ws://localhost:9120/websocketserver", on_message_callback=self.on_message
        )
        self.ws_client.write_message(self.message)
    
    def on_message(self, message):
        message = json.loads(message)

        if "move" in message:
            print("N-Puzzle PlannerClient: ")
            print(message)
            self.ws_server.write_message(json.dumps(message))

class NPuzzleWSServer(tornado.websocket.WebSocketHandler):
    def open(self):
        global n_puzzle_ws_server
        n_puzzle_ws_server = self
        print("[N-Puzzle WS Server py]: Connection established")
    
    def on_message(self, message):
        message = json.loads(message)
        print("N-Puzzle: ")
        print(message)

        if "gameTileMatrix" in message:
            PlannerWSClient(json.dumps(message), self)
        #elif "pose" in message:
        #    if message["pose"] == "win":
        #        pepper.victory()
        #    elif message["pose"] == "lose":
        #        pepper.sad()

    def on_close(self):
        print("[N-Puzzle WS Server py]: Connection closed")
  
    def on_ping(self, data):
        print("ping received: %s" %(data))
  
    def on_pong(self, data):
        print("pong received: %s" %(data))
  
    def check_origin(self, origin):
        return True

def main_loop(data):
    global run

    while (run):
        time.sleep(1.)

def main():
    global run

    t = threading.Thread(target=main_loop, args=(None,))
    t.start()

    npuzzle_web_app = tornado.web.Application([
        (r"/websocketserver", NPuzzleWSServer)
    ])
    npuzzle_http_server = tornado.httpserver.HTTPServer(npuzzle_web_app)
    npuzzle_http_server.listen(9020)
    print("[N-Puzzle App py]: N-Puzzle WS server listening on port 9020")

    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print("[N-Puzzle App py]: ---KeyboardInterrupt--- Quitting N-Puzzle WS server...")
    
    if n_puzzle_ws_server is not None:
        try:
            n_puzzle_ws_server.write_message(json.dumps({"command": "close"}))
            n_puzzle_ws_server.close()
        except tornado.websocket.WebSocketClosedError:
            pass
    print("[N-Puzzle App py]: N-Puzzle WS server quit")
    run = False

if __name__ == "__main__":
    main()
