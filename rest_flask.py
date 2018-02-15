import requests
from flask import Flask
import subprocess


app = Flask(__name__)


@app.route('/')
def site():
    # TODO
    return 'Controller App Client\n\n' + \
            'Number of Switches: http://localhost:8008/switches' + \
            'Switches Data:      http://127.0.0.1:8080/topology/switches/curl' + \
            'Links Data:         http://127.0.0.1:8080/topology/links/curl'+ \
            'Hosts Data:         http://127.0.0.1:8080/topology/hosts/curl'

@app.route('/switches')
def switches_dp():
    r = requests.get('http://127.0.0.1:8080/switches')
    return r.json()

@app.route('/switches/curl')
def switches_dp_curl():
    data = subprocess.check_output('curl -X GET http://127.0.0.1:8080/switches', shell = True)
    print(data)
    return data

@app.route('/topology/switches')
def topo_switches():
    r = requests.get('http://127.0.0.1:8080/topology/switches')
    return r.json()

@app.route('/topology/switches/curl')
def topo_switches_curl():
    data = subprocess.check_output('curl -X GET http://127.0.0.1:8080/topology/switches',shell = True)
    print(data)
    return data

@app.route('/topology/links')
def topo_links():
    r = requests.get('http://127.0.0.1:8080/topology/links')
    return r.json()

@app.route('/topology/links/curl')
def topo_links_curl():
    data = subprocess.check_output('curl -X GET http://127.0.0.1:8080/topology/links',shell = True)
    print(data)
    return data

@app.route('/topology/hosts')
def topo_hosts():
    r = requests.get('http://127.0.0.1:8080/topology/hosts')
    return r.json()

@app.route('/topology/hosts/curl')
def topo_hosts_curl():
    data = subprocess.check_output('curl -X GET http://127.0.0.1:8080/topology/hosts',shell = True)
    print(data)
    return data

if __name__ == '__main__':
    app.run(debug=True, port=8008)