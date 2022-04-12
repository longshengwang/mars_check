# -*- coding:utf-8 -*-

from resource import Resource
from constants import DEVICE_CONFIG_NAME


class DeviceConfigs(Resource):
    name = DEVICE_CONFIG_NAME

    devices_config = {}

    url = "/mars/v1/devices/config"

    def __init__(self, mars_config):
        Resource.__init__(self, mars_config)

    def init_all_devices(self):
        self.devices_config = self.get(self.url)['configs']
        return self.devices_config

    def get_device_name(self, device_id):
        for device in self.devices_config:
            if device['id'] == device_id:
                return device['name']

        return device_id

    def get_data(self):
        return self.devices_config

    def set_data(self, configs):
        self.devices_config = configs

    @classmethod
    def initialize(cls, mars_config):
        c = cls(mars_config)
        c.init_all_devices()
        return c

    @classmethod
    def initialize_with(cls, mars_config, configs):
        c = cls(mars_config)
        c.set_data(configs)
        return c
