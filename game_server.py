import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket
import os
import sys
import json
import numpy as np

sys.path.append(os.getenv("PEPPER_TOOLS_HOME") + "/cmd_server")
sys.path.append("pepper")
sys.path.append("blackjack")
import blackjack_agent
import pepper_cmd
import blackjack_pepper

from tornado.websocket import websocket_connect

websocket_server = None

def convertValue(value):
    if value in ['J','Q','K']:
        return 10
    elif value == 'A':
        return 1
    else: return value

def usable_ace(hand):
        return int(1 in hand and sum(hand) + 10 <= 21)
    
def sum_hand(hand):
        sum_hand_ = sum(hand)

        return sum_hand_ + 10 if usable_ace(hand) else sum_hand_

class MyWebSocketServer(tornado.websocket.WebSocketHandler):
    def open(self):
        global websocket_server
        websocket_server = self
    
    def on_message(self, message):
        global agent, pepper
        message = json.loads(message)
        if('gameState' in message):
            bankCardValue = message['gameState']['bankCardValues'][0]
            bankCardValue = convertValue(bankCardValue)
            playerCardValues = message['gameState']['playerCardValues']
            playerCardValues = list(map(convertValue,playerCardValues))
            obs = (
                sum_hand(playerCardValues),
                bankCardValue,
                usable_ace(playerCardValues)
            ) 
            action = agent.act(obs)
            self.write_message(json.dumps({'action': action}))

        elif('command' in message):
            if(message['command']== 'win'):
                pepper.victory()
            elif(message['command']=='lose'):
                pepper.sad()

    def on_close(self):
        print 'Connection closed'
  
    def on_ping(self, data):
        print 'ping received: %s' %(data)
  
    def on_pong(self, data):
        print 'pong received: %s' %(data)
  
    def check_origin(self, origin):
        return True

def main():
    global agent, pepper
    learning_rate = 0.01
    n_episodes = 2
    start_epsilon = 1.0
    epsilon_decay = start_epsilon / (n_episodes / 2) 
    final_epsilon = 0.1
    
    pepper_cmd.begin()
    pepper = blackjack_pepper.BlackjackPepper()
    
    agent = blackjack_agent.BlackjackAgent(
        learning_rate = learning_rate,
        initial_epsilon = start_epsilon,
        epsilon_decay = epsilon_decay,  
        final_epsilon = final_epsilon
    )

    agent.q_values = np.loadtxt('blackjack_q_values/q_values_5M.txt')
    
    application = tornado.web.Application([
        (r'/websocketserver',MyWebSocketServer),])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen('9020')
    print "Websocket server listening on port 9020"

    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print "-- Keyboard interrupt --"

    print websocket_server
    if (not websocket_server is None):
        websocket_server.close()
    print "Web server quit."   

if __name__ == "__main__":
    main()