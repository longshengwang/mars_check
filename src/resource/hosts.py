# -*- coding:utf-8 -*-
from constants import HOSTS_NAME
from resource import Resource


class Hosts(Resource):
    # {
    #    "hosts":
    #       [
    #           {"id":"24:6E:96:05:07:4D/None","mac":"24:6E:96:05:07:4D","vlan":"None","innerVlan":"None","outerTpid":"unknown","configured":false,"ipAddresses":["192.168.60.119"],"locations":[{"elementId":"of:0000b86a97145100","port":"1"}]},
    #           {"id":"A8:2B:B5:78:1F:D4/None","mac":"A8:2B:B5:78:1F:D4","vlan":"None","innerVlan":"None","outerTpid":"unknown","configured":true,"ipAddresses":[],"locations":[{"elementId":"of:0000b86a97145100","port":"25"}]},
    #           {"id":"90:E2:BA:24:A0:86/None","mac":"90:E2:BA:24:A0:86","vlan":"None","innerVlan":"None","outerTpid":"unknown","configured":false,"ipAddresses":["192.168.0.63"],"locations":[{"elementId":"of:0000b86a97145100","port":"27"}]},
    #           {"id":"90:E2:BA:24:A1:34/None","mac":"90:E2:BA:24:A1:34","vlan":"None","innerVlan":"None","outerTpid":"unknown","configured":false,"ipAddresses":["192.168.10.83"],"locations":[{"elementId":"of:0000b86a97145100","port":"28"}]}
    #       ]
    # }
    name = HOSTS_NAME
    hosts = {}
    mars_config = None
    url = "/mars/v1/hosts"

    def __init__(self, mars_config):
        Resource.__init__(self, mars_config)

    def init_all_hosts(self):
        self.hosts = self.get(self.url)['hosts']
        return self.hosts

    def get_data(self):
        return self.hosts

    def get_ip(self, mac):
        for host_item in self.hosts:
            if host_item['mac'] == mac:
                ip_addr = host_item['ipAddresses']
                if len(ip_addr) > 0:
                    return ','.join(ip_addr)
        return None

    def set_data(self, hosts):
        self.hosts = hosts

    @property
    def uni_key(self):
        return 'id'

    @property
    def compare_key(self):
        return ['ipAddresses', 'locations', 'lastUpdateTime']

    @classmethod
    def initialize(cls, mars_config):
        c = cls(mars_config)
        c.init_all_hosts()
        return c

    @classmethod
    def initialize_with(cls, mars_config, hosts):
        c = cls(mars_config)
        c.set_data(hosts)
        return c
