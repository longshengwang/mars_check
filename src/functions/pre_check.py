# -*- coding: utf-8 -*-
import devices
import flows
import hosts
from lib.printer import print_warn, print_normal
from utils import flow_to_line_string, group_to_line_string


class PreCheck:
    mars_config = None
    device_config_object = None
    flow_object = None
    group_object = None
    host_object = None

    def __init__(self, mars_config):
        self.mars_config = mars_config

    def _get_data(self):
        self.device_config_object = devices.DeviceConfigs.initialize(self.mars_config)
        self.flow_object = flows.Flows.initialize(self.mars_config)
        self.group_object = flows.Groups.initialize(self.mars_config)
        self.host_object = hosts.Hosts.initialize(self.mars_config)

    def _check_if_contains_pending_flow(self):
        all_flows = self.flow_object.get_data()
        is_print_header = False
        for flow in all_flows:
            if flow['state'] != 'ADDED':
                if not is_print_header:
                    is_print_header = True
                    print_warn('')
                    print_warn('[ WARN ]FOUND pending flows ====>')
                self._print_pending_flow(flow)
        if is_print_header:
            print_warn('<==== FOUND pending flows')

    def _check_if_contains_pending_group(self):
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
        pass

    def check(self):
        print_normal('Going to check all the data.')
        self._get_data()
        self._check_if_contains_pending_flow()
        self._check_if_contains_pending_group()

        print_normal('Check Finish.')

    def _print_pending_flow(self, flow):
        res = flow_to_line_string(flow, self.host_object, self.device_config_object)
        print_warn(res)

    def _print_pending_group(self, group):
        res = group_to_line_string(group, self.device_config_object)
        print_warn(res)
