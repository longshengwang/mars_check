# -*- coding:utf8 -*-

from resource import Resource


class Flows(Resource):
    name = 'flows'
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
