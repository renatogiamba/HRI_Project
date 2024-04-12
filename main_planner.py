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
import pddl_planning

planner_ws_server = None
run = True

class PlannerWSServer(tornado.websocket.WebSocketHandler):
    def open(self):
        global planner_ws_server
        planner_ws_server = self
        print("[Planner WS Server py]: Connection established")
    
    def on_message(self, message):
        message = json.loads(message)

        if "gameTileMatrix" in message:
            problem = pddl_planning.generate_N_puzzle(message["gameTileMatrix"])
            moves = pddl_planning.solve_N_puzzle(problem)
            first_move = moves[1]
            tile = int(first_move.split("(")[1].split(",")[0].split("_")[1])
            self.write_message(json.dumps({"move": tile}))

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

    planner_web_app = tornado.web.Application([
        (r"/websocketserver", PlannerWSServer)
    ])
    planner_http_server = tornado.httpserver.HTTPServer(planner_web_app)
    planner_http_server.listen(9120)
    print("[Planner App py]: Planner WS server listening on port 9120")

    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print("[Planner App py]: ---KeyboardInterrupt--- Quitting Planner WS server...")
    
    if planner_ws_server is not None:
        try:
            planner_ws_server.write_message(json.dumps({"command": "close"}))
            planner_ws_server.close()
        except tornado.websocket.WebSocketClosedError:
            pass
    print("[Planner App py]: Planner WS server quit")
    run = False

if __name__ == "__main__":
    main()
