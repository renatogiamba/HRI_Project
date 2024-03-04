import json
import numpy
import os
import sys
import time
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web

sys.path.append(os.getenv("PEPPER_TOOLS_HOME") + "/cmd_server")
sys.path.append("blackjack")
sys.path.append("pepper")
import pepper_cmd
import blackjack_agent
import blackjack_pepper

pepper_ws_server = None
blackjack_ws_server = None
survey_ws_server = None

class PepperWSServer(tornado.websocket.WebSocketHandler):
    @tornado.gen.coroutine
    def open(self):
        global pepper_ws_server
        pepper_ws_server = self
        print '[Pepper WS Server py]: Connection established'
    
    @tornado.gen.coroutine
    def on_message(self, message):
        global pepper

        message = json.loads(message)

        if "state" in message:
            if message["state"] == "ready":
                self.write_message(json.dumps({"scene": "waiting"}))
            elif message["state"] == "waiting":
                time.sleep(5.)
                _, _ = pepper.scan_for_person(1.2, False)
                pepper.reset_sonars()
                self.write_message(json.dumps({"scene": "backPersonScanned"}))
            elif message["state"] == "waiting2":
                time.sleep(5.)
                _, _ = pepper.scan_for_person(1.2, True)
                pepper.reset_sonars()
                self.write_message(json.dumps({"scene": "frontPersonScanned"}))
            elif message["state"] == "person scanned":
                pepper.hello()
                self.write_message(json.dumps({"scene": "welcome"}))
            elif message["state"] == "person welcomed":
                if message["buttonPressed"] == "Yes":
                    pepper.victory()
                    self.write_message(json.dumps({"scene": "presentation"}))
                elif message["buttonPressed"] == "No":
                    pepper.sad()
                    self.write_message(json.dumps({"scene": "noGame"}))
            elif message["state"] == "person presented":
                self.write_message(json.dumps({"scene": "everPlayed"}))
            elif message["state"] == "person played":
                if message["buttonPressed"] == "Yes":
                    self.write_message(json.dumps({"scene": "recap"}))
                elif message["buttonPressed"] == "No":
                    self.write_message(json.dumps({"scene": "rules"}))
            elif message["state"] == "rules recap":
                if message["buttonPressed"] == "Yes":
                    self.write_message(json.dumps({"scene": "rules"}))
                elif message["buttonPressed"] == "No":
                    self.write_message(json.dumps({"command": "game"}))
            elif message["state"] == "got rules":
                self.write_message(json.dumps({"command": "game"}))
        elif "say" in message:
            pepper.say(message["say"])

    @tornado.gen.coroutine
    def on_close(self):
        print '[Pepper WS Server py]: Connection closed'
  
    @tornado.gen.coroutine
    def on_ping(self, data):
        print 'ping received: %s' %(data)
  
    @tornado.gen.coroutine
    def on_pong(self, data):
        print 'pong received: %s' %(data)
  
    @tornado.gen.coroutine
    def check_origin(self, origin):
        return True

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

class BlackjackWSServer(tornado.websocket.WebSocketHandler):
    @tornado.gen.coroutine
    def open(self):
        global blackjack_ws_server
        blackjack_ws_server = self
        print '[Pepper Blackjack WS Server py]: Connection established'
    
    @tornado.gen.coroutine
    def on_message(self, message):
        global pepper, agent

        message = json.loads(message)

        if "gameState" in message:
            bankCardValue = message["gameState"]["bankCardValues"][0]
            bankCardValue = convertValue(bankCardValue)
            playerCardValues = message["gameState"]["playerCardValues"]
            playerCardValues = list(map(convertValue,playerCardValues))
            obs = (
                sum_hand(playerCardValues),
                bankCardValue,
                usable_ace(playerCardValues)
            ) 
            action = agent.act(obs)
            self.write_message(json.dumps({"action": action}))
        elif "pose" in message:
            if message["pose"] == "win":
                pepper.victory()
            elif message["command"] == "lose":
                pepper.sad()

    @tornado.gen.coroutine
    def on_close(self):
        print '[Pepper Blackjack WS Server py]: Connection closed'
  
    @tornado.gen.coroutine
    def on_ping(self, data):
        print 'ping received: %s' %(data)
  
    @tornado.gen.coroutine
    def on_pong(self, data):
        print 'pong received: %s' %(data)
  
    @tornado.gen.coroutine
    def check_origin(self, origin):
        return True

class SurveyWSServer(tornado.websocket.WebSocketHandler):
    @tornado.gen.coroutine
    def open(self):
        global survey_ws_server
        survey_ws_server = self
        print '[Pepper Survey WS Server py]: Connection established'
    
    @tornado.gen.coroutine
    def on_message(self, message):
        message = json.loads(message)

        if "state" in message:
            if message["state"] == "survey collected":
                f = open("surveys/surveys_db.jsonl", mode="a")
                f.write(json.dumps({
                    "interactionRate": message["interactionRate"],
                    "recommendationRate": message["recommendationRate"],
                    "review": message["review"]
                }) + "\n")
                f.close()

    @tornado.gen.coroutine
    def on_close(self):
        print '[Pepper Survey WS Server py]: Connection closed'
  
    @tornado.gen.coroutine
    def on_ping(self, data):
        print 'ping received: %s' %(data)
  
    @tornado.gen.coroutine
    def on_pong(self, data):
        print 'pong received: %s' %(data)
  
    @tornado.gen.coroutine
    def check_origin(self, origin):
        return True

if __name__ == "__main__":
    global pepper

    pepper_cmd.begin()

    pepper = blackjack_pepper.BlackjackPepper()

    learning_rate = 0.01
    n_episodes = 2
    start_epsilon = 1.0
    epsilon_decay = start_epsilon / (n_episodes / 2) 
    final_epsilon = 0.1
    agent = blackjack_agent.BlackjackAgent(
        learning_rate = learning_rate,
        initial_epsilon = start_epsilon,
        epsilon_decay = epsilon_decay,  
        final_epsilon = final_epsilon
    )
    agent.q_values = numpy.loadtxt('blackjack_q_values/q_values_5M.txt')

    time.sleep(5.)

    pepper_web_app = tornado.web.Application([
        (r"/websocketserver", PepperWSServer)
    ])
    pepper_http_server = tornado.httpserver.HTTPServer(pepper_web_app)
    pepper_http_server.listen("9050")
    print "[Pepper App py]: Pepper WS server listening on port 9050"

    blackjack_web_app = tornado.web.Application([
        (r"/websocketserver", BlackjackWSServer)
    ])
    blackjack_http_server = tornado.httpserver.HTTPServer(blackjack_web_app)
    blackjack_http_server.listen("9020")
    print "[Pepper App py]: Pepper Blakcjack WS server listening on port 9020"

    survey_web_app = tornado.web.Application([
        (r"/websocketserver", SurveyWSServer)
    ])
    survey_http_server = tornado.httpserver.HTTPServer(survey_web_app)
    survey_http_server.listen("9030")
    print "[Pepper App py]: Pepper Survey WS server listening on port 9030"

    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print "[Pepper App py]: ---KeyboardInterrupt--- Quitting Pepper WS server..."
        print "[Pepper App py]: ---KeyboardInterrupt--- Quitting Pepper Blackjack WS server..."
        print "[Pepper App py]: ---KeyboardInterrupt--- Quitting Pepper Survey WS server..."
    
    if pepper_ws_server is not None:
        try:
            if pepper_ws_server is not None:
                pepper_ws_server.write_message(json.dumps({"command": "close"}))
                pepper_ws_server.close()
        except tornado.websocket.WebSocketClosedError:
            pass
        try:
            if blackjack_ws_server is not None:
                blackjack_ws_server.write_message(json.dumps({"command": "close"}))
                blackjack_ws_server.close()
        except tornado.websocket.WebSocketClosedError:
            pass
        try:
            if survey_ws_server is not None:
                survey_ws_server.write_message(json.dumps({"command": "close"}))
                survey_ws_server.close()
        except tornado.websocket.WebSocketClosedError:
            pass
    print "[Pepper App py]: Pepper WS server quit"
    print "[Pepper App py]: Pepper Blackjack WS server quit"
    print "[Pepper App py]: Pepper Survey WS server quit"

    pepper_cmd.end()
