import os
import json
import psutil

from wsgiref.simple_server import make_server

from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config


project_path = os.path.dirname(os.path.abspath(__file__))

def home(request):
    template = os.path.join(project_path, "static", "templates", "index.html")
    return Response(open(template).read())

def process(request):
    name = request.matchdict.get('name')
    pid = [pid for pid in psutil.get_pid_list()
                       if psutil.Process(pid).name == name][0]
    proc = psutil.Process(pid)
    print name, pid
    return Response(json.dumps(
        proc.get_cpu_percent(interval=1)
        ))

if __name__ == '__main__':
    config = Configurator()
    config.add_route('home', '/')
    config.add_view(home, route_name='home')
    config.add_route('process', '/process/{name}')
    config.add_view(process, route_name='process')
    config.add_static_view(name='static', path='static/')

    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()