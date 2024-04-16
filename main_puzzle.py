import json
import numpy
import os
import sys
import time
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import pddl_planning

n_puzzle_ws_server = None
run = True

class NPuzzleWSServer(tornado.websocket.WebSocketHandler):
    @tornado.gen.coroutine
    def open(self):
        global n_puzzle_ws_server
        n_puzzle_ws_server = self
        self.pepper_ws_server = yield tornado.websocket.websocket_connect(
            "ws://localhost:9050/websocketserver",
            callback=self.on_message
        )
        print("[N-Puzzle WS Server py]: Connection established")
    
    @tornado.gen.coroutine
    def on_message(self, message):
        message = json.loads(message)

        if "gameTileMatrix" in message:
            problem = pddl_planning.generate_N_puzzle(message["gameTileMatrix"])
            moves = pddl_planning.solve_N_puzzle(problem, message["timeout"])
            if len(moves) < 2:
                self.write_message(json.dumps({"move": 0}))
                return
            first_move = moves[1]
            tile = int(first_move.split("(")[1].split(",")[0].split("_")[1])
            first_move = first_move.replace("(", "").replace(")", "").split(", ")
            i_old = int(first_move[1])
            j_old = int(first_move[2])
            i_new = int(first_move[3])
            j_new = int(first_move[4])

            if i_new - i_old == -1:
                self.pepper_ws_server.write_message(json.dumps({
                    "say": f"I suggest: slide tile {tile} up..."
                }))
                self.pepper_ws_server.write_message(json.dumps({"pose": "slide up"}))
            elif i_new - i_old == 1:
                self.pepper_ws_server.write_message(json.dumps({
                    "say": f"I suggest: slide tile {tile} down..."
                }))
                self.pepper_ws_server.write_message(json.dumps({"pose": "slide down"}))
            elif j_new - j_old == -1:
                self.pepper_ws_server.write_message(json.dumps({
                    "say": f"I suggest: slide tile {tile} left..."
                }))
                self.pepper_ws_server.write_message(json.dumps({"pose": "slide left"}))
            elif j_new - j_old == 1:
                self.pepper_ws_server.write_message(json.dumps({
                    "say": f"I suggest: slide tile {tile} right..."
                }))
                self.pepper_ws_server.write_message(json.dumps({"pose": "slide right"}))
            self.write_message(json.dumps({"move": tile}))
        elif "pose" in message:
            if message["pose"] == "win":
                #pass
                self.pepper_ws_server.write_message(json.dumps({"pose": "win"}))
            #

    @tornado.gen.coroutine
    def on_close(self):
        self.pepper_ws_server.close()
        print("[N-Puzzle WS Server py]: Connection closed")
  
    @tornado.gen.coroutine
    def on_ping(self, data):
        print("ping received: %s" %(data))
  
    @tornado.gen.coroutine
    def on_pong(self, data):
        print("pong received: %s" %(data))
  
    @tornado.gen.coroutine
    def check_origin(self, origin):
        return True

def main():
    global run

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
