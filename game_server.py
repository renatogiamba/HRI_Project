import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket
import os
import sys
import json

sys.path.append(os.getenv("PEPPER_TOOLS_HOME") + "/cmd_server")
sys.path.append("pepper")
import blackjack_agent

from tornado.websocket import websocket_connect

websocket_server = None

class MyWebSocketServer(tornado.websocket.WebSocketHandler):
    def open(self):
        global websocket_server
        websocket_server = self
    
    def on_message(self, message):
        global agent
        obs = json.loads(message)
        action = agent.act(obs)
        self.write_message(json.dumps({'answer': action}))

    def on_close(self):
        print 'Connection closed'
  
    def on_ping(self, data):
        print 'ping received: %s' %(data)
  
    def on_pong(self, data):
        print 'pong received: %s' %(data)
  
    def check_origin(self, origin):
        return True

def main():
    global agent
    
    agent = blackjack_agent.BlackjackAgent()
    
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