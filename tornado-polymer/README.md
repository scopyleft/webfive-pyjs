# Tornado + Polymer for web5 conference

**Rendering a CPU graph through websockets using Shadow DOM elements.**

`Tornado` (Python) is serving data retrieved by `psutil` (Python) via websockets.
`gRahaeljs` (JavaScript) is drawing a line graph of this data updated via 
`Polymer` (JavaScript) and rendered through reusable Shadow DOM elements.

## Usage

    $ pip install -r requirements.txt
    $ git clone git://github.com/Polymer/polymer.git --recursive static/polymer-all
    $ python server.py
    go to http://localhost:8888/
    click the button and enjoy!

## Ressources

* http://www.polymer-project.org/
* http://www.tornadoweb.org/en/stable/
* http://g.raphaeljs.com/
* https://pypi.python.org/pypi/psutil/
