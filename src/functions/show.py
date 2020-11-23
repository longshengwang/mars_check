# -*- coding:utf8 -*-
from lib.color import UseStyle
from lib.printer import print_normal, print_normal_start, print_normal_center, print_normal_end
from resource import DeviceConfigs, Links, Hosts
from utils import device_to_line_string, format_time_string_2_number, get_devices_configs, link_to_line_string, \
    get_link, host_to_line_string, get_host


class ShowResource:
    mars_config = None

    def __init__(self, mars_config):
        self.mars_config = mars_config

    def show_online_devices(self):
        print_normal('Show the ' + UseStyle('ONLINE', fore='green', mode='underline') + ' devices.')
        devices_config_obj = DeviceConfigs.initialize(mars_config=self.mars_config)
        for device_config in devices_config_obj.get_data():
            print_normal(device_to_line_string(device_config))

    def show_snap_devices(self, snap_time):
        snap_time_str = format_time_string_2_number(snap_time)
        print_normal('Show the ' + UseStyle(snap_time, fore='green', mode='underline') + ' devices.')
        devices_config_obj = DeviceConfigs.initialize_with(self.mars_config,
                                                           get_devices_configs(self.mars_config, snap_time_str))

        for device_config in devices_config_obj.get_data():
            print_normal(device_to_line_string(device_config))

    def show_online_links(self):
        print_normal('Show the ' + UseStyle('ONLINE', fore='green', mode='underline') + ' links.')
        link_obj = Links.initialize(mars_config=self.mars_config)
        devices_config_obj = DeviceConfigs.initialize(mars_config=self.mars_config)
        for device_config in devices_config_obj.get_data():
            print_normal_start('Device Name : ' + device_config['name'], color='yellow')
            for link in link_obj.get_data():
                if link['src']['device'] == device_config['id']:
                    print_normal_center(link_to_line_string(link, devices_config_obj))
            print_normal_end('')
            print_normal('')

    def show_snap_links(self, snap_time_str):
        snap_time = format_time_string_2_number(snap_time_str)
        print_normal('Show the ' + UseStyle(snap_time_str, fore='green', mode='underline') + ' links.')

        link_obj = Links.initialize_with(self.mars_config, get_link(self.mars_config, snap_time))
        devices_config_obj = DeviceConfigs.initialize_with(self.mars_config,
                                                           get_devices_configs(self.mars_config, snap_time))

        for device_config in devices_config_obj.get_data():
            print_normal_start('Device Name : ' + device_config['name'], color='yellow')
            for link in link_obj.get_data():
                if link['src']['device'] == device_config['id']:
                    print_normal_center(link_to_line_string(link, devices_config_obj))
            print_normal_end('')
            print_normal('')

    def show_online_hosts(self):
        print_normal('Show the ' + UseStyle('ONLINE', fore='green', mode='underline') + ' hosts.')
        host_obj = Hosts.initialize(mars_config=self.mars_config)
        devices_config_obj = DeviceConfigs.initialize(mars_config=self.mars_config)

        for device_config in devices_config_obj.get_data():
            print_normal_start('Device Name : ' + device_config['name'], color='yellow')
            for host in host_obj.get_data():
                for location in host['locations']:
                    if location['elementId'] == device_config['id']:
                        print_normal_center(host_to_line_string(host, devices_config_obj))

            print_normal_end('')
            print_normal('')

    def show_snap_hosts(self, snap_time_str):
        print_normal('Show the ' + UseStyle(snap_time_str, fore='green', mode='underline') + ' hosts.')

        snap_time = format_time_string_2_number(snap_time_str)
        host_obj = Hosts.initialize_with(self.mars_config, get_host(self.mars_config, snap_time))
        devices_config_obj = DeviceConfigs.initialize_with(self.mars_config,
                                                           get_devices_configs(self.mars_config, snap_time))

        for device_config in devices_config_obj.get_data():
            print_normal_start('Device Name : ' + device_config['name'], color='yellow')
            for host in host_obj.get_data():
                for location in host['locations']:
                    if location['elementId'] == device_config['id']:
                        print_normal_center(host_to_line_string(host, devices_config_obj))

            print_normal_end('')
            print_normal('')
