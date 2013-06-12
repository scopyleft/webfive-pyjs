import os
import sys
import json
import time

import psutil

from tornado import httpserver, ioloop, web, websocket

SERVER_PATH = os.path.abspath(os.path.dirname(__file__))
STATIC_PATH = os.path.join(SERVER_PATH, 'static')

settings = {
    "static_path": STATIC_PATH,
    "server_name": "localhost",
    "debug": True,
}

connections = []


class MainHandler(web.RequestHandler):
    def get(self):
        self.render("static/templates/index.html",
                    server_name=settings['server_name'])


class GlobalCPUWSHandler(websocket.WebSocketHandler):

    def on_message(self, message):
        for i in range(21):
            data = {
                'x': i,
                'y': psutil.cpu_percent(interval=1)
            }
            self.write_message(json.dumps(data))
            time.sleep(1)


class FirefoxCPUWSHandler(websocket.WebSocketHandler):

    def on_message(self, message):
        firefox_pid = [pid for pid in psutil.get_pid_list()
                       if psutil.Process(pid).name == "firefox"][0]
        firefox_process = psutil.Process(firefox_pid)
        for i in range(21):
            data = {
                'x': i,
                'y': firefox_process.get_cpu_percent(interval=1.0)
            }
            self.write_message(json.dumps(data))
            time.sleep(1)


application = web.Application([
    (r'/', MainHandler),
    (r'/cpu/global', GlobalCPUWSHandler),
    (r'/cpu/firefox', FirefoxCPUWSHandler),
    (r"/", web.StaticFileHandler,
        dict(path=settings['static_path'])),
], **settings)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        settings['server_name'] = sys.argv[1]
    http_server = httpserver.HTTPServer(application)
    http_server.listen(8888)
    ioloop.IOLoop.instance().start()
