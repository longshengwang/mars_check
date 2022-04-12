# -*- coding: utf-8 -*-
from lib.color import UseStyle
from lib.printer import print_warn, print_normal, print_normal_start, print_normal_center, print_normal_end
from resource import DeviceConfigs, Flows, Groups, Hosts
from utils import flow_to_line_string, group_to_line_string, get_devices_configs, get_flow, get_host, get_group, \
    host_to_line_string
import time

CORE_DEFAULT_FLOW_SIZE = 4


class Check:
    mars_config = None
    device_config_object = None
    flow_object = None
    group_object = None
    host_object = None

    def __init__(self, mars_config):
        self.mars_config = mars_config

    def check_online(self):
        print_normal('Going to check the ' + UseStyle('ONLINE', fore='green', mode='underline') + ' data.')
        self._get_online_data()
        self._check_if_contains_pending_flow()
        self._check_if_contains_pending_group()
        self._check_default_flow()
        self._check_if_host_has_ip()
        print_normal('Check Finish.')

    def _get_online_data(self):
        self.device_config_object = DeviceConfigs.initialize(self.mars_config)
        self.flow_object = Flows.initialize(self.mars_config)
        self.group_object = Groups.initialize(self.mars_config)
        self.host_object = Hosts.initialize(self.mars_config)

    def check_snap(self, snap_time):
        snap_time_str = str(int(time.mktime(time.strptime(snap_time, '%Y-%m-%d %H:%M:%S'))))
        print_normal('Going to check the snap ' + UseStyle(snap_time, fore='green', mode='underline') + ' data.')
        self._get_snap_data(snap_time_str)

        self._check_if_contains_pending_flow()
        self._check_if_contains_pending_group()
        self._check_default_flow()
        self._check_if_host_has_ip()
        print_normal('Check Finish.')

    def _get_snap_data(self, snap_time):
        self.device_config_object = DeviceConfigs.initialize_with(self.mars_config,
                                                                  get_devices_configs(self.mars_config, snap_time))
        self.flow_object = Flows.initialize_with(self.mars_config,
                                                 get_flow(self.mars_config, snap_time))
        self.group_object = Groups.initialize_with(self.mars_config, get_group(self.mars_config, snap_time))
        self.host_object = Hosts.initialize_with(self.mars_config,
                                                 get_host(self.mars_config, snap_time))

    def _check_if_contains_pending_flow(self):
        print_normal("1. Start to check if contains pending flow.")
        all_flows = self.flow_object.get_data()
        is_print_header = False
        for flow in all_flows:
            if flow['state'] != 'ADDED':
                if not is_print_header:
                    is_print_header = True
                    print_normal_start('[ WARN ] FOUND pending flows.', color='red')
                self._print_pending_flow(flow)
        if is_print_header:
            print_normal_end('', color='red')

    def _check_if_contains_pending_group(self):
        print_normal("2. Start to check if contains pending group.")
        all_groups = self.group_object.get_data()
        is_print_header = False
        for group in all_groups:
            if group['state'] != 'ADDED':
                if not is_print_header:
                    is_print_header = True
                    print_normal_start('[ WARN ] FOUND pending groups ====>', color='red')
                self._print_pending_group(group)
        if is_print_header:
            print_normal_end('', color='red')

    # core flow
    def _check_default_flow(self):
        print_normal("3. Start to check default flow of core app.")
        all_flows = self.flow_object.get_data()
        device_flow_dict = {}
        for flow_item in all_flows:
            device_id = flow_item['deviceId']
            if device_flow_dict.get(device_id) is None:
                device_flow_dict[device_id] = []

            if flow_item['appId'] == 'org.onosproject.core':
                instructions = flow_item['treatment']['instructions']
                criteria = flow_item['selector']['criteria']
                if len(instructions) == 1 \
                        and instructions[0]['type'] == 'OUTPUT' \
                        and instructions[0]['port'] == 'CONTROLLER' \
                        and len(criteria) == 1 \
                        and criteria[0]['type'] == 'ETH_TYPE' \
                        and (criteria[0]['ethType'] == '0x800'
                             or criteria[0]['ethType'] == '0x88cc'
                             or criteria[0]['ethType'] == '0x8942'
                             or criteria[0]['ethType'] == '0x806'):
                    device_flow_dict[device_id].append(flow_item)
        # check
        keys = device_flow_dict.keys()
        for device_id in keys:
            if len(device_flow_dict[device_id]) != CORE_DEFAULT_FLOW_SIZE:

                print_normal_start('[ ERROR ] Device Name: ' + self.device_config_object.get_device_name(device_id) +
                                   '; The default flow from core app may miss some one [IPv4, LLDP, ARP, BDDP].',  color='red')
                for item in device_flow_dict[device_id]:
                    print_normal_center(flow_to_line_string(item, self.host_object, self.device_config_object),  color='red')
                print_normal_end(' ', color='red')

    def _check_if_host_has_ip(self):
        print_normal("4. Start to check if the host has ip address.")
        has_found_warn = False
        for host in self.host_object.get_data():
            if host['ipAddresses'] is None or len(host['ipAddresses']) == 0:
                if not has_found_warn:
                    has_found_warn = True
                    print_normal_start("[ WARN ] Found No Ip Host", color='red')
                print_normal_center(host_to_line_string(host, self.device_config_object), color='red')

        if has_found_warn:
            print_normal_end(' ', color='red')

    def _print_pending_flow(self, flow):
        res = flow_to_line_string(flow, self.host_object, self.device_config_object)
        print_normal_center(res, color='red')

    def _print_pending_group(self, group):
        res = group_to_line_string(group, self.device_config_object)
        print_normal_center(res, color='red')
