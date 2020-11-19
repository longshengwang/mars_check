# -*- coding:utf-8 -*-

import time
import os
from resource import Devices, DeviceConfigs, Flows, Groups, Hosts, Links
from lib.printer import print_normal


class SnapData:
    mars_config = None

    def __init__(self, mars_config):
        self.mars_config = mars_config

    def snap_all_data(self):
        print_normal('Going to snap all the data from ' + self.mars_config.get_url())
        device_object = Devices.initialize(self.mars_config)
        device_config_object = DeviceConfigs.initialize(self.mars_config)
        host_object = Hosts.initialize(self.mars_config)
        flow_object = Flows.initialize(self.mars_config)
        group_object = Groups.initialize(self.mars_config)
        link_object = Links.initialize(self.mars_config)

        t = int(time.time())

        data_path = self.mars_config.get_base_path() + '/' + str(t)

        os.mkdir(data_path)
        device_object.save(data_path)
        device_config_object.save(data_path)
        host_object.save(data_path)
        flow_object.save(data_path)
        group_object.save(data_path)
        link_object.save(data_path)

        print_normal('Success to snap the data')
