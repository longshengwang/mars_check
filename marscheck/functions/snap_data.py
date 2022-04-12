# -*- coding:utf-8 -*-

import os
import shutil
import time

from constants import DEVICE_NAME, DEVICE_CONFIG_NAME, GROUPS_NAME, FLOW_NAME, HOSTS_NAME, LINKS_NAME
from lib.printer import print_normal
from resource import Devices, DeviceConfigs, Flows, Groups, Hosts, Links
from utils import get_link, get_host, get_group, get_flow, get_devices, get_devices_configs


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

    def get_summary(self):
        res = []
        path_dir = self.mars_config.get_base_path()
        snap_times_list = os.listdir(path_dir)
        snap_times_list.sort(reverse=True)

        for snap_time in snap_times_list:
            try:
                time_stamp = int(snap_time)
                time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time_stamp))
                cur_summary = {
                    'time': time_str,
                    GROUPS_NAME: len(get_group(self.mars_config, snap_time)),
                    DEVICE_NAME: len(get_devices(self.mars_config, snap_time)),
                    DEVICE_CONFIG_NAME: len(get_devices_configs(self.mars_config, snap_time)),
                    HOSTS_NAME: len(get_host(self.mars_config, snap_time)),
                    LINKS_NAME: len(get_link(self.mars_config, snap_time)),
                    FLOW_NAME: len(get_flow(self.mars_config, snap_time)),
                }
                res.append(cur_summary)
            except ValueError, e:
                pass

        return res

    def delete(self, selectors):
        parsed_times = [str(int(time.mktime(time.strptime(i, '%Y-%m-%d %H:%M:%S')))) for i in selectors]
        for item in parsed_times:
            shutil.rmtree(self.mars_config.get_base_path() + item)
