import json
from ryu.app import ofctl_rest
from ryu.app import simple_switch_13
from ryu.controller import dpset, ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from webob import Response
from ryu.app.wsgi import ControllerBase, WSGIApplication, route
from ryu.topology.api import get_switch, get_link, get_host
from ryu.topology import event
from ryu.lib import dpid as dpid_lib

simple_switch_instance_name = 'simple_switch_api_app'
url_sw = '/switches'
url_topo = '/topology/'


class ControllerApp (simple_switch_13.SimpleSwitch13):

    _CONTEXTS = {'wsgi': WSGIApplication,'dpset': dpset.DPSet}

    def __init__(self, *args, **kwargs):
        super(ControllerApp, self).__init__(*args, **kwargs)
        # Stores DPSet instance to call its API in this app
        self.switches = {}
        wsgi = kwargs['wsgi']
        self.dpset = kwargs['dpset']
        wsgi.register(SwitchREST,
                      {simple_switch_instance_name: self})
        wsgi.register(TopologyREST, {'topology_api_app': self})


class SwitchREST(ControllerBase,ControllerApp):

    def __init__(self, req, link, data, **config):
        super(SwitchREST, self).__init__(req, link, data, **config)
        self.simple_switch_app = data[simple_switch_instance_name]

    @route('switchstats', url_sw, methods=['GET'])
    def switch_number_info(self, req,**kwargs):

        simple_switch = self.simple_switch_app
        dp = simple_switch.dpset.get_all()
        data = dict(dp)
        body = json.dumps(str(data))
        print(type(body))
        if dp is None:
            self.logger.info('No such datapath')
            return Response(status=404)
        return Response(content_type='application/json', body=body)


class TopologyREST(ControllerBase):

    def __init__(self, req, link, data, **config):
        super(TopologyREST, self).__init__(req, link, data, **config)
        self.topology_api_app = data['topology_api_app']

    @route('topo', url_topo + 'links', methods=['GET'])
    def topo_links(self, req, **kwargs):
        dpid = None
        if 'dpid' in kwargs:
            dpid = dpid_lib.str_to_dpid(kwargs['dpid'])
        links = get_link(self.topology_api_app, dpid)
        # print(str(links))
        body = json.dumps([link.to_dict() for link in links])
        return Response(content_type='application/json', body=body)

    @route('topo', url_topo + 'switches', methods=['GET'])
    def topo_switches(self, req, **kwargs):
        dpid = None
        if 'dpid' in kwargs:
            dpid = dpid_lib.str_to_dpid(kwargs['dpid'])
        switches = get_switch(self.topology_api_app, dpid)
        body = json.dumps([switch.to_dict() for switch in switches])
        # print(type(body))
        return Response(content_type='application/json', body=body)

    @route('topo', url_topo + 'hosts', methods=['GET'])
    def topo_hosts(self, req, **kwargs):
        dpid = None
        if 'dpid' in kwargs:
            dpid = dpid_lib.str_to_dpid(kwargs['dpid'])
        hosts = get_host(self.topology_api_app, dpid)
        body = json.dumps([host.to_dict() for host in hosts])
        return Response(content_type='application/json', body=body)