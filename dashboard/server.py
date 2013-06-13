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

def process_all(request):
    value = psutil.cpu_percent(interval=.5)
    return Response(json.dumps(value))

def process(request):
    name = request.matchdict.get('name')
    pid = [pid for pid in psutil.get_pid_list()
                       if psutil.Process(pid).name == name][0]
    if pid:
        proc = psutil.Process(pid)
        value = proc.get_cpu_percent(interval=.5)
    else:
        value = 0
    return Response(json.dumps(value))

if __name__ == '__main__':
    config = Configurator()
    config.add_route('home', '/')
    config.add_view(home, route_name='home')
    config.add_route('process_all', '/process')
    config.add_view(process_all, route_name='process_all')
    config.add_route('process', '/process/{name}')
    config.add_view(process, route_name='process')
    config.add_static_view(name='static', path='static/')

    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()