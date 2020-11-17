# -*- coding:utf8 -*-

import time
import devices
import flows
import hosts
import os


class SnapData:
    mars_config = None

    def __init__(self, mars_config):
        self.mars_config = mars_config

    def snap_all_data(self):
        print 'Going to snap all the data from ' + self.mars_config.get_url()
        device_object = devices.Devices.initialize(self.mars_config)
        device_config_object = devices.DeviceConfigs.initialize(self.mars_config)
        host_object = hosts.Hosts.initialize(self.mars_config)
        flow_object = flows.Flows.initialize(self.mars_config)
        group_object = flows.Groups.initialize(self.mars_config)

        t = int(time.time())

        data_path = self.mars_config.get_base_path() + '/' + str(t)

        os.mkdir(data_path)
        device_object.save(data_path)
        device_config_object.save(data_path)
        host_object.save(data_path)
        flow_object.save(data_path)
        group_object.save(data_path)

        print 'Success to snap the data'
