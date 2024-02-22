import json
import os
import sys
import time
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web

sys.path.append(os.getenv("PEPPER_TOOLS_HOME") + "/cmd_server")
sys.path.append("pepper")
import pepper_cmd
import blackjack_pepper

pepper_ws_server = None

class BlackjackPepperSocketServer(tornado.websocket.WebSocketHandler):
    @tornado.gen.coroutine
    def open(self):
        global pepper_ws_server
        pepper_ws_server = self
        print '[Pepper WS Server py]: Connection established'
    
    @tornado.gen.coroutine
    def on_message(self, message):
        pass

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
    loop = True
    while loop:
        front_person_scanned = False
        back_person_scanned = False
        person_scanned = False

        while not person_scanned:
            front_person_scanned, back_person_scanned = pepper.scan_for_person(
                1.2, True
            )
            pepper.reset_sonars()
            person_scanned = front_person_scanned or back_person_scanned

            if front_person_scanned:
                pepper.on_front_person_scanned()
                loop = False
            if back_person_scanned:
                pepper.on_back_person_scanned()
                time.sleep(3.)

    web_app = tornado.web.Application([
        (r"/websocketserver", BlackjackPepperSocketServer)
    ])
    http_server = tornado.httpserver.HTTPServer(web_app)
    http_server.listen("9050")
    print "[Pepper App py]: WS server listening on port 9050"

    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print "[Pepper App py]: ---KeyboardInterrupt--- Quitting WS server..."
    
    if pepper_ws_server is not None:
        pepper_ws_server.write_message(json.dumps({"command": "close"}))
        pepper_ws_server.close()
    print "[Pepper App py]: WS server quit"

    pepper_cmd.end()