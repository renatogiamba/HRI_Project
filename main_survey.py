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

survey_ws_server = None
run = True

class SurveyWSServer(tornado.websocket.WebSocketHandler):
    @tornado.gen.coroutine
    def open(self):
        global survey_ws_server
        survey_ws_server = self
        self.pepper_ws_server = yield tornado.websocket.websocket_connect(
            "ws://localhost:9050/websocketserver",
            callback=self.on_message
        )
        print("[Pepper Survey WS Server py]: Connection established")
    
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
        elif "say" in message:
            self.pepper_ws_server.write_message(json.dumps(message))
            self.pepper_ws_server.write_message(json.dumps({"pose": "hello"}))


    @tornado.gen.coroutine
    def on_close(self):
        self.pepper_ws_server.close()
        print("[Pepper Survey WS Server py]: Connection closed")
  
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

    survey_web_app = tornado.web.Application([
        (r"/websocketserver", SurveyWSServer)
    ])
    survey_http_server = tornado.httpserver.HTTPServer(survey_web_app)
    survey_http_server.listen(9030)
    print("[Survey App py]: Survey WS server listening on port 9030")

    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print("[Survey App py]: ---KeyboardInterrupt--- Quitting Survey WS server...")
    
    if survey_ws_server is not None:
        try:
            survey_ws_server.write_message(json.dumps({"command": "close"}))
            survey_ws_server.close()
        except tornado.websocket.WebSocketClosedError:
            pass
    print("[Survey App py]: Survey WS server quit")
    run = False

if __name__ == "__main__":
    main()
