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
class NPuzzleWSServer(tornado.websocket.WebSocketHandler):
    @tornado.gen.coroutine
    def open(self):
        global n_puzzle_ws_server
        n_puzzle_ws_server = self
        print('[Pepper N-Puzzle WS Server py]: Connection established')
    
    @tornado.gen.coroutine
    def on_message(self, message):

        message = json.loads(message)

        if "gameTileMatrix" in message:
            problem = pddl_planning.generate_N_puzzle(message["gameTileMatrix"])
            moves = pddl_planning.solve_N_puzzle(problem)
            #bankCardValue = convertValue(bankCardValue)
            #playerCardValues = message["gameState"]["playerCardValues"]
            #playerCardValues = list(map(convertValue,playerCardValues))
            #obs = (
            #    sum_hand(playerCardValues),
            #    bankCardValue,
            #    usable_ace(playerCardValues)
            #) 
            #action = agent.act(obs)
            #pepper.say("I suggest: " + ("Stand" if action == 0 else "Hit"))
            #self.write_message(json.dumps({"action": action}))
        #elif "pose" in message:
        #    if message["pose"] == "win":
        #        pepper.victory()
        #    elif message["pose"] == "lose":
        #        pepper.sad()

    @tornado.gen.coroutine
    def on_close(self):
        print('[Pepper N-Puzzle WS Server py]: Connection closed')
  
    @tornado.gen.coroutine
    def on_ping(self, data):
        print('ping received: %s' %(data))
  
    @tornado.gen.coroutine
    def on_pong(self, data):
        print('pong received: %s' %(data))
  
    @tornado.gen.coroutine
    def check_origin(self, origin):
        return True