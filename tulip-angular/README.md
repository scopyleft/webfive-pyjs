# Tulip + Angular for web5 conference

**A basic chat using WebSockets.**

`Flask` (Python3.3) is serving both http and websocket handlers using
`Tulip` and `websockets` (Python3.3) rendered using `AngularJS` (JavaScript).

All Python3.3 dependencies have been put directly in the repo for
simplicity and lack of knowledge regarding Python3's packaging/virtualenv
(+cutting edge versions of flask/jinja2/werkzeug).

## Usage

Launch both

    $ python3.3 websockets_server.py
    $ python3.3 server.py 

Go to http://127.0.0.1:8080/

    fill your message and click send!

## Ressources

* https://code.google.com/p/tulip/
* https://github.com/aaugustin/websockets
* https://github.com/mitsuhiko/flask
* https://github.com/mitsuhiko/jinja2
* https://github.com/mitsuhiko/itsdangerous
* https://github.com/mitsuhiko/werkzeug
* http://angularjs.org/
