# -*- coding: utf-8 -*-
from lib.color import UseStyle
from lib.printer import print_warn, print_normal
from resource import DeviceConfigs, Flows, Groups, Hosts
from utils import flow_to_line_string, group_to_line_string, get_devices_configs, get_flow, get_host, get_group
import time

CORE_DEFAULT_FLOW_SIZE = 4


class PreCheck:
    mars_config = None
    device_config_object = None
    flow_object = None
    group_object = None
    host_object = None

    def __init__(self, mars_config):
        self.mars_config = mars_config

    def check_online(self):
        print_normal('Going to check the >> ' + UseStyle('online', fore='green') + ' << data.')
        self._get_online_data()
        self._check_if_contains_pending_flow()
        self._check_if_contains_pending_group()
        self._check_default_flow()
        print_normal('Check Finish.')

    def _get_online_data(self):
        self.device_config_object = DeviceConfigs.initialize(self.mars_config)
        self.flow_object = Flows.initialize(self.mars_config)
        self.group_object = Groups.initialize(self.mars_config)
        self.host_object = Hosts.initialize(self.mars_config)

    def check_snap(self, snap_time):
        snap_time_str = str(int(time.mktime(time.strptime(snap_time, '%Y-%m-%d %H:%M:%S'))))
        print_normal('Going to check the snap >> ' + UseStyle(snap_time, fore='green') + ' << data.')
        self._get_snap_data(snap_time_str)

        self._check_if_contains_pending_flow()
        self._check_if_contains_pending_group()
        self._check_default_flow()
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
                    print_warn('')
                    print_warn('[ WARN ] FOUND pending flows.')
                self._print_pending_flow(flow)
        # if is_print_header:
        #     print_warn('<==== FOUND pending flows')

    def _check_if_contains_pending_group(self):
        print_normal("2. Start to check if contains pending group.")
        all_groups = self.group_object.get_data()
        is_print_header = False
        for group in all_groups:
            if group['state'] != 'ADDED':
                if not is_print_header:
                    is_print_header = True
                    print_warn('')
                    print_warn('[ WARN ]FOUND pending groups ====>')
                self._print_pending_group(group)
        if is_print_header:
            print_warn('<==== FOUND pending groups')

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
                print_warn('')
                print_warn('>> SWITCH ' + self.device_config_object.get_device_name(device_id) +
                           ' << The default flow from core app may miss some one [IPv4, LLDP, ARP, BDDP].')
                for item in device_flow_dict[device_id]:
                    print_warn(flow_to_line_string(item, self.host_object, self.device_config_object))

    def _print_pending_flow(self, flow):
        res = flow_to_line_string(flow, self.host_object, self.device_config_object)
        print_warn(res)

    def _print_pending_group(self, group):
        res = group_to_line_string(group, self.device_config_object)
        print_warn(res)
