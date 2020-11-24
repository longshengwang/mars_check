# -*- coding:utf-8 -*-
from constants import DEVICE_NAME
from resource import Resource


class Devices(Resource):
    name = DEVICE_NAME

    devices = {}
    mars_config = None
    url = "/mars/v1/devices"

    def __init__(self, mars_config):
        Resource.__init__(self, mars_config)

    def init_all_devices(self):
        self.devices = self.get(self.url)['devices']
        return self.devices

    def get_data(self):
        return self.devices

    @property
    def uni_key(self):
        return 'id'

    @property
    def compare_key(self):
        return ['annotations', 'available']

    @classmethod
    def initialize(cls, mars_config):
        c = cls(mars_config)
        c.init_all_devices()
        return c
