import json
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
import blackjack_pepper

pepper_ws_server = None
blackjack_ws_server = None

class PepperWSServer(tornado.websocket.WebSocketHandler):
    @tornado.gen.coroutine
    def open(self):
        global pepper_ws_server
        pepper_ws_server = self
        print '[Pepper WS Server py]: Connection established'
    
    @tornado.gen.coroutine
    def on_message(self, message):
        message = json.loads(message)

        if "state" in message:
            if message["state"] == "ready":
                self.write_message(json.dumps({"scene": "waiting"}))
            elif message["state"] == "ready survey":
                self.write_message(json.dumps({"scene": "survey"}))
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

if __name__ == "__main__":
    global pepper

    pepper_cmd.begin()

    pepper = blackjack_pepper.BlackjackPepper()

    time.sleep(5.)

    pepper_web_app = tornado.web.Application([
        (r"/websocketserver", PepperWSServer)
    ])
    http_server = tornado.httpserver.HTTPServer(pepper_web_app)
    http_server.listen("9050")
    print "[Pepper App py]: Pepper WS server listening on port 9050"

    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print "[Pepper App py]: ---KeyboardInterrupt--- Quitting Pepper WS server..."
    
    if pepper_ws_server is not None:
        try:
            pepper_ws_server.write_message(json.dumps({"command": "close"}))
            pepper_ws_server.close()
        except tornado.websocket.WebSocketClosedError:
            pass
    print "[Pepper App py]: Pepper WS server quit"

    pepper_cmd.end()