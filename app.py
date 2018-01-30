import http.client
import json
from flask import Flask, request
from ryu.lib import ofctl_v1_5
# from flask_restful import Resource, Api
from ryu.topology.api import get_switch
from ryu.base import app_manager
from ryu.app.wsgi import ControllerBase
from ryu.app.wsgi import Response
from ryu.app.wsgi import WSGIApplication
from ryu.lib import dpid as dpid_lib

app = Flask(__name__)


# REST command template


# def rest_command(func):
#     def _rest_command(*args, **kwargs):
#         try:
#             msg = func(*args, **kwargs)
#             return Response(content_type='application/json',
#                             body=json.dumps(msg))
#
#         except SyntaxError as e:
#             status = 400
#             details = e.msg
#         except (ValueError, NameError) as e:
#             status = 400
#             details = e.message
#
#         return Response(status=status, body=json.dumps(msg))
#
#     return _rest_command


### RYU ###

class TopologyAPI(app_manager.RyuApp):
    _CONTEXTS = {
        'wsgi': WSGIApplication
    }

    def __init__(self, *args, **kwargs):
        super(TopologyAPI, self).__init__(*args, **kwargs)

        wsgi = kwargs['wsgi']
        wsgi.register(TopologyController, {'topology_api_app': self})


class RyuNetworkData(ControllerBase):

    def __init__(self, req, data, **config):
        super(RyuNetworkData, self).__init__(req, **config)
        self.dpset = data['dpset']

    # GET /stats/switches
    @app.route("/stats/switches", methods=["GET"])
    def switch_number(self, **kwargs):
        dps = list(self.dpset.dps.keys())
        body = json.dumps(dps)
        return Response(content_type='application/json', body=body)

    # GET stats/desc/<dpid>
    @app.route("/stats/desc/<dpid>", methods=["GET"], requirements={'dpid': dpid_lib.DPID_PATTERN})
    def switch_stats(self, req, **kwargs):
        stats = ofctl_v1_5.get_desc_stats(req)
        return json.dumps(stats)


class TopologyController(ControllerBase):
    def __init__(self, req, link, data, **config):
        super(TopologyController, self).__init__(req, link, data, **config)
        self.topology_api_app = data['topology_api_app']

    def _switches(self, req, **kwargs):
        dpid = None
        if 'dpid' in kwargs:
            dpid = dpid_lib.str_to_dpid(kwargs['dpid'])
        switches = get_switch(self.topology_api_app, dpid)
        body = json.dumps([switch.to_dict() for switch in switches])
        return Response(content_type='application/json', body=body)

    # GET /v1.0/topology/switches
    @app.route('/v1.0/topology/switches', methods=["GET"])
    def topo(self, req, **kwargs):
        topo = self._switches(req, **kwargs)
        return json.dumps(topo)

### Floodlight ###

class StaticFlowPusher(object):

    def __init__(self, server):
        self.server = server

    def get(self, data):
        ret = self.rest_call({}, 'GET')
        return json.loads(ret[2])

    def rest_call(self, data, action):
        path = '/wm/staticflowpusher/json'
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
        }
        body = json.dumps(data)
        conn = http.client.HTTPConnection(self.server, 8080)
        conn.request(action, path, body, headers)
        response = conn.getresponse()
        ret = (response.status, response.reason, response.read())
        print(ret)
        conn.close()
        return ret

# Floodlight controller connection
pusher = StaticFlowPusher('127.0.0.1:6653')


if __name__ == '__main__':
    app.run(debug=True, port=8080)
