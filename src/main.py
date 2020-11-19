# -*- coding:utf-8 -*-

import os
import argparse
from os.path import expanduser

from config import MarsConfig
from functions.compare import ResourceCompare
from functions.pre_check import PreCheck
from functions.snap_data import SnapData
from lib.command_selector import CommandSelector
from functions.compare import compare_flows, compare_groups, compare_hosts, compare_link
from utils import flow_to_line_string, group_to_line_string, host_to_line_string
from lib.printer import print_normal, print_warn, print_normal_center, print_normal_end, print_normal_start
from lib.color import UseStyle

DEFAULT_CONFIG_PATH = '/.mars_check/'
MAX_BACKUP_COUNT = 20

mars_config = MarsConfig("https://210.63.204.28", 'karaf', 'karaf', expanduser("~") + DEFAULT_CONFIG_PATH)


def snap(args):
    snap = SnapData(mars_config)
    snap.snap_all_data()


def compare(args):
    resource_compare = ResourceCompare(mars_config)
    snap_times = resource_compare.get_all_snap_time()
    cmd_selector = CommandSelector(snap_times, 'Please select two time to compare.', 2)
    selectors = cmd_selector.get_selector()
    if selectors is None:
        return

    selectors.sort(reverse=True)
    print_normal('After  Time is ' + selectors[0])

    print_normal('Before Time is ' + selectors[1])
    print_normal('')

    before_time, after_time = resource_compare.load(selectors)

    if args.flow:
        print_normal('====  FLOWS COMPARE ====')
        # resource_compare.compare_flow()
        before_flow = resource_compare.get_flow(before_time)
        after_flow = resource_compare.get_flow(after_time)
        res = compare_flows(before_flow, after_flow)
        keys = res.keys()
        for key in keys:
            device_name = resource_compare.device_config_object.get_device_name(key)
            if args.device is not None and (device_name != args.device and device_name != args.device):
                continue
            print_normal(UseStyle('Device Name: ' + device_name, fore='yellow'))
            # print_normal(UseStyle('Device Name: ' + device_name + ' ====> Added', fore='yellow'))
            print_normal_start('')
            print_normal_center('=> Added')
            changes_json = res[key]
            if len(changes_json['added']) > 0:
                for item in changes_json['added']:
                    print_normal_center(flow_to_line_string(item, resource_compare.host_object, resource_compare.device_config_object), 'green')

            print_normal_center('=> Removed')
            if changes_json['removed'] and len(changes_json['removed']) > 0:
                for item in changes_json['removed']:
                    print_normal_center(flow_to_line_string(item, resource_compare.host_object, resource_compare.device_config_object), 'red')

            print_normal_end('')
            print_normal('')
    elif args.group:
        print_normal('====  GROUPS COMPARE ====')
        before_group = resource_compare.get_group(before_time)
        after_group = resource_compare.get_group(after_time)
        res = compare_groups(before_group, after_group)
        keys = res.keys()
        for key in keys:
            device_name = resource_compare.device_config_object.get_device_name(key)
            if args.device is not None and (device_name != args.device and device_name != args.device):
                continue
            print_normal(UseStyle('Device Name: ' + device_name, fore='yellow'))
            # print_normal(UseStyle('Device Name: ' + device_name + ' ====> Added', fore='yellow'))
            print_normal_start('')
            print_normal_center('=> Added')
            changes_json = res[key]
            if len(changes_json['added']) > 0:
                for item in changes_json['added']:
                    print_normal_center(group_to_line_string(item, resource_compare.device_config_object), 'green')

            # print_normal(UseStyle('Device Name: ' + device_name + ' ====> Removed', fore='yellow'))
            print_normal_center('=> Removed')
            if changes_json['removed'] and len(changes_json['removed']) > 0:
                for item in changes_json['removed']:
                    print_normal_center(group_to_line_string(item, resource_compare.device_config_object), 'red')
            print_normal_end('')
            print_normal('')
    elif args.host:
        print_normal('====  Host COMPARE ====')
        before_host = resource_compare.get_host(before_time)
        after_host = resource_compare.get_host(after_time)
        res = compare_hosts(before_host, after_host, resource_compare.device_config_object)

        print_normal_start('')
        print_normal_center('--- Added')
        if len(res['added']) > 0:
            for item in res['added']:
                print_normal_center(host_to_line_string(item, resource_compare.device_config_object), 'green')

        # print_normal(UseStyle('Device Name: ' + device_name + ' ====> Removed', fore='yellow'))
        print_normal_center('--- Removed')
        if res['removed'] and len(res['removed']) > 0:
            for item in res['removed']:
                print_normal_center(host_to_line_string(item, resource_compare.device_config_object), 'red')

        print_normal_center('--- Modified')
        if res['modified'] and len(res['modified']) > 0:
            for item in res['modified']:
                print_normal_center(str(item), 'cyan')
        print_normal_end('')
        print_normal('')
    elif args.link:
        pass



def pre_check(args):
    pre_check = PreCheck(mars_config)
    pre_check.check()


def show_devices(args):
    print 'show devices'


class DeviceIdAction(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        super(DeviceIdAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        print 'values ', values
        setattr(namespace, self.dest, values)


def run():
    init_config_dir()
    parser = argparse.ArgumentParser(description="Mars Check Tool")
    # group = parser.add_mutually_exclusive_group(required=True)
    # group.add_argument('snap', help='Save the data of now.')
    # group.add_argument('--check', action='store_true', help='Check the flow/group data if correct.')
    # group.add_argument('--compare', action='store_true', help='Compare the different time data.')

    sub_parsers = parser.add_subparsers()
    device_args = sub_parsers.add_parser('devices', help='Show all the devices info.')
    device_args.set_defaults(func=show_devices)
    snap_args = sub_parsers.add_parser('snap', help='Save the data of now.')
    snap_args.set_defaults(func=snap)

    check_args = sub_parsers.add_parser('check', help='Check the flow/group data if correct.')
    check_args.set_defaults(func=pre_check)

    compare_args = sub_parsers.add_parser('compare', help='Compare the different time data.')
    compare_args.add_argument('-d', '--device', help='Specify device for flow or group.')
    group = compare_args.add_mutually_exclusive_group(required=True)
    group.add_argument('-l', '--link', action='store_true', help='Only compare link data.')
    group.add_argument('-f', '--flow', action='store_true', help='Only compare flow data.')
    group.add_argument('-g', '--group', action='store_const', const='all', help='Only compare group data.')
    group.add_argument('-ho', '--host', action='store_true', help='Only compare host data.')
    # group.add_argument('-a', '--all', action='store_true', help='Compare all data.')
    compare_args.set_defaults(func=compare)

    # argcomplete.autocomplete(parser)
    args = parser.parse_args()
    args.func(args)


def init_config_dir():
    home = expanduser("~")
    if not os.path.exists(home + DEFAULT_CONFIG_PATH):
        os.mkdir(home + DEFAULT_CONFIG_PATH)


if __name__ == '__main__':
    # mars_config = MarsConfig("https://210.63.204.28", 'karaf', 'karaf', expanduser("~") + DEFAULT_CONFIG_PATH)
    # cmp = ResourceCompare(mars_config)
    #

    # cmp.get_all_snap_time()

    run()
    #
    # path = '/home/wls/.mars_check/1605694695/flows'
    # f = open(path, 'r')
    # lines = f.readlines()
    # ss = ''.join(lines)
    #
    # import json
    # obj = json.loads(ss)
    # print obj

    # i = 0
    # l = ['2010-12-31 12:52:30.000','2010-12-31 03:15:30.000', '2010-12-31 22:22:30.000']
    # cmd_selector = CommandSelector(l, 'Please select two time to compare.', 2)
    # selectors = cmd_selector.get_selector()
    # if selectors is not None:
    #     print 'Now compare the value \n    ' + selectors[0] + '\n    ' + selectors[1]
