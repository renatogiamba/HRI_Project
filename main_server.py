import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket
import os
import sys
import json
import time

sys.path.append(os.getenv("PEPPER_TOOLS_HOME") + "/cmd_server")
sys.path.append("pepper")
import pepper_cmd
import blackjack_pepper

from tornado.websocket import websocket_connect

websocket_server = None

class MyWebSocketServer(tornado.websocket.WebSocketHandler):
    def open(self):
        global websocket_server
        websocket_server = self
    
    def on_message(self, message):
        global pepper

        if(message == 'First Interaction'):
            self.write_message(json.dumps({'answer': 'First Start'}))
        
        elif('interface started' in message):
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
                if back_person_scanned:
                    pepper.on_back_person_scanned()
                time.sleep(1.)
            self.write_message(json.dumps({'answer': 'start'}, indent=4))

    
    def on_close(self):
        print 'Connection closed'
  
    def on_ping(self, data):
        print 'ping received: %s' %(data)
  
    def on_pong(self, data):
        print 'pong received: %s' %(data)
  
    def check_origin(self, origin):
        return True

def main():
    global pepper
    
    pepper_cmd.begin()
    pepper = blackjack_pepper.BlackjackPepper()
    
    application = tornado.web.Application([
        (r'/websocketserver',MyWebSocketServer),])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen('9050')
    print "Websocket server listening on port 9050"

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