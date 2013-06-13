# Pyramid + Polymer dashboard for web5 conference

**Rendering CPU graphs through websockets using Shadow DOM elements.**

`Pyramid` (Python) is serving data retrieved by `psutil` (Python) via AJAX.
`ChartJS` (JavaScript) is drawing a line graph of this data updated via 
`Polymer` (JavaScript) and rendered through reusable Shadow DOM elements.

## Usage

    $ pip install -r requirements.txt
    $ git clone git://github.com/Polymer/polymer.git --recursive static/polymer
    $ python server.py
    go to http://localhost:8080/
    just enjoy!

## Ressources

* http://www.polymer-project.org/
* http://www.pylonsproject.org/
* http://www.chartjs.org/
* https://pypi.python.org/pypi/psutil/
