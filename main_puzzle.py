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
    def open(self):
        global n_puzzle_ws_server
        n_puzzle_ws_server = self
        print("[N-Puzzle WS Server py]: Connection established")
    
    def on_message(self, message):
        message = json.loads(message)

        if "gameTileMatrix" in message:
            print("[N-Puzzle WS Server py]: Start planning...")
            problem = pddl_planning.generate_N_puzzle(message["gameTileMatrix"])
            opt = len(message["gameTileMatrix"]) == 3
            moves = pddl_planning.solve_N_puzzle(problem, opt)
            print("[N-Puzzle WS Server py]: Planning finished...")
            if len(moves) < 2:
                self.write_message(json.dumps({"move": 0}))
                return
            first_move = moves[1]
            tile = int(first_move.split("(")[1].split(",")[0].split("_")[1])
            self.write_message(json.dumps({"move": tile}))
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
