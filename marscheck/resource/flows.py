# -*- coding:utf-8 -*-
from constants import FLOW_NAME
from resource import Resource


class Flows(Resource):
    name = FLOW_NAME
    flows = {}
    mars_config = None
    url = "/mars/v1/flows"

    def __init__(self, mars_config):
        Resource.__init__(self, mars_config)

    def init_all_flows(self):
        self.flows = self.get(self.url)['flows']
        return self.flows

    def get_data(self):
        return self.flows

    def set_data(self, data):
        self.flows = data

    @property
    def uni_key(self):
        return 'id'

    @property
    def compare_key(self):
        return ['state']

    @classmethod
    def initialize(cls, mars_config):
        c = cls(mars_config)
        c.init_all_flows()
        return c

    @classmethod
    def initialize_with(cls, mars_config, flows):
        c = cls(mars_config)
        c.set_data(flows)
        return c