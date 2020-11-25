# -*- coding:utf8 -*-
from lib.color import UseStyle
from lib.command_single_selector import CommandSingleSelector
from resource import DeviceConfigs, Links, Flows, Hosts, Groups
from utils import get_devices_configs, get_flow, get_link, get_host, get_group, get_all_snap_time, \
    format_time_string_2_number, flow_to_line_string
from model.flow_path import find_path, find_flows


def _print_host(host, host_type):
    host_str = host['mac']
    if len(host['ipAddresses']) > 0:
        host_str = host_str + ' (' + ', '.join(host['ipAddresses']) + ')'

    print 'The ' + UseStyle(host_type, fore='green') + ' host is ' + UseStyle(host_str, fore='green')

class Trace:
    mars_config = None

    src_mac = None
    dst_mac = None
    gateway = None
    snap_time = None

    device_config_obj = None
    hosts_obj = None
    flow_obj = None
    group_obj = None
    link_obj = None

    def __init__(self, mars_config):
        self.mars_config = mars_config

    def init_online_data(self):
        print 'Start to trace the ' + UseStyle('ONLINE', fore='green', mode='underline') + ' data'
        self.device_config_obj = DeviceConfigs.initialize(self.mars_config)
        self.hosts_obj = Hosts.initialize(self.mars_config)
        self.group_obj = Groups.initialize(self.mars_config)
        self.flow_obj = Flows.initialize(self.mars_config)
        self.link_obj = Links.initialize(self.mars_config)

    def init_snap_data(self, snap_time_str):
        print 'Start to trace the ' + UseStyle(snap_time_str, fore='green', mode='underline') + ' snap data\n'
        snap_time = format_time_string_2_number(snap_time_str)
        self.snap_time = snap_time
        self.device_config_obj = DeviceConfigs.initialize_with(self.mars_config,
                                                               get_devices_configs(self.mars_config, snap_time))
        self.hosts_obj = Hosts.initialize_with(self.mars_config, get_host(self.mars_config, snap_time))
        self.group_obj = Groups.initialize_with(self.mars_config, get_group(self.mars_config, snap_time))
        self.flow_obj = Flows.initialize_with(self.mars_config, get_flow(self.mars_config, snap_time))
        self.link_obj = Links.initialize_with(self.mars_config, get_link(self.mars_config, snap_time))

    def get_path(self):
        print ''

        hosts = self.hosts_obj.get_data()
        src_host = filter(lambda x: x['mac'] == self.src_mac, hosts)[0]
        dst_host = filter(lambda x: x['mac'] == self.dst_mac, hosts)[0]

        _print_host(src_host, 'SRC')
        _print_host(dst_host, 'DST')

        try:
            if self.gateway is None:
                paths = find_path(self.flow_obj.get_data(), self.link_obj.get_data(), self.group_obj.get_data(),
                                  src_host,
                                  dst_host)
                print '\nThe Path is : '
                self._print_paths(src_host, dst_host, paths)
            else:
                gateway = filter(lambda x: x['mac'] == self.gateway, hosts)[0]

                _print_host(gateway, 'GATEWAY')

                paths1 = find_path(self.flow_obj.get_data(), self.link_obj.get_data(), self.group_obj.get_data(),
                                   src_host,
                                   gateway)
                print '\nThe Path from SRC to GATEWAY is : '
                self._print_paths(src_host, gateway, paths1, is_dst_gateway=True)
                paths2 = find_path(self.flow_obj.get_data(), self.link_obj.get_data(), self.group_obj.get_data(),
                                   gateway,
                                   dst_host)

                print 'The Path from GATEWAY to DST is : '
                self._print_paths(gateway, dst_host, paths2, is_src_gateway=True)
        except Exception, e:
            print UseStyle(e.message, fore='red')

    def select_src_host(self):
        host_str_list = [
            host['mac'] + ('(' + ','.join(host['ipAddresses']) + ')' if len(host['ipAddresses']) > 0 else '')
            for host in self.hosts_obj.get_data()
        ]
        # snap_times = get_all_snap_time(self.mars_config)
        cmd_selector = CommandSingleSelector(host_str_list, 'Please select the src host.')
        selector_str = cmd_selector.get_selector()
        self.src_mac = selector_str.split('(')[0]
        print 'The selected ' + UseStyle('SRC', fore='green') + ' host is ' + UseStyle(selector_str, fore='green')

    def select_dst_host(self):
        host_str_list = [
            host['mac'] + ('(' + ','.join(host['ipAddresses']) + ')' if len(host['ipAddresses']) > 0 else '')
            for host in self.hosts_obj.get_data()
        ]
        cmd_selector = CommandSingleSelector(host_str_list, 'Please select the dst host.')
        selector_str = cmd_selector.get_selector()
        self.dst_mac = selector_str.split('(')[0]
        print 'The selected ' + UseStyle('DST', fore='green') + ' host is ' + UseStyle(selector_str, fore='green')

    def select_gateway(self):
        no_gateway_str = 'NO GATEWAY'
        host_str_list = [
            host['mac'] + ('(' + ','.join(host['ipAddresses']) + ')' if len(host['ipAddresses']) > 0 else '')
            for host in self.hosts_obj.get_data()
        ]
        host_str_list.insert(0, no_gateway_str)
        cmd_selector = CommandSingleSelector(host_str_list, 'Please select the gateway host.')
        selector_str = cmd_selector.get_selector()
        if no_gateway_str == selector_str:
            print UseStyle('NO GATEWAY', fore='green')
        else:
            self.gateway = selector_str.split('(')[0]
            print 'The selected ' + UseStyle('GATEWAY', fore='green') + ' is ' + UseStyle(selector_str, fore='green')

    def get_host_mac(self, ip_or_mac):
        for host in self.hosts_obj.get_data():
            if host['mac'] == ip_or_mac:
                return host['mac']

            for ip in host['ipAddresses']:
                if ip == ip_or_mac:
                    return host['mac']

        return None

    def _print_paths(self, src_host, dst_host, paths, is_dst_gateway=False, is_src_gateway=False):
        print UseStyle(
            '[GATEWAY]' if is_src_gateway else (src_host['mac'] + '(' + ','.join(src_host['ipAddresses']) + ')'),
            fore='yellow'),

        first_link_word = ' X '

        for location in src_host['locations']:
            if location['elementId'] == paths[0].flow['deviceId'] and location['port'] == paths[0].in_port:
                first_link_word = '==>'

        if first_link_word == ' X ':
            print UseStyle(first_link_word, fore='red'),
        else:
            print UseStyle(first_link_word, fore='green'),

        for path in paths:
            device_name = self.device_config_obj.get_device_name(path.flow['deviceId'])

            link_sign = UseStyle(' ==>', fore='green')
            if path.flow['state'] != 'ADDED':
                link_sign = UseStyle(' ==>', fore='red')

            print UseStyle(path.in_port + '| ' + device_name + ' |' + path.out_port, fore='yellow',
                           mode='underline') + link_sign,

        last_path = paths[-1]
        is_last_path_connect_dst = False
        for location in dst_host['locations']:
            if location['elementId'] == last_path.flow['deviceId'] and location['port'] == last_path.out_port:
                is_last_path_connect_dst = True

        if not is_last_path_connect_dst:
            print UseStyle(' X ', fore='red'),

        print UseStyle(
            '[GATEWAY]' if is_dst_gateway else (dst_host['mac'] + '(' + ','.join(dst_host['ipAddresses']) + ')'),
            fore='yellow')
