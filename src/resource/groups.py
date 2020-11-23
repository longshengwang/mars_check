# -*- coding:utf-8 -*-
from constants import GROUPS_NAME

from resource import Resource


class Groups(Resource):
    name = GROUPS_NAME

    groups = {}
    mars_config = None
    url = "/mars/v1/groups"

    def __init__(self, mars_config):
        Resource.__init__(self, mars_config)

    def init_all_groups(self):
        self.groups = self.get(self.url)['groups']
        return self.groups

    def get_data(self):
        return self.groups

    def set_data(self, data):
        self.groups = data

    @property
    def uni_key(self):
        return ['id', 'deviceId']

    @property
    def compare_key(self):
        return ['state']

    @classmethod
    def initialize(cls, mars_config):
        c = cls(mars_config)
        c.init_all_groups()
        return c

    @classmethod
    def initialize_with(cls, mars_config, groups):
        c = cls(mars_config)
        c.set_data(groups)
        return c
