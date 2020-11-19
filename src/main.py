# -*- coding:utf-8 -*-

import os
import argparse
from os.path import expanduser

from config import MarsConfig
from functions.compare import ResourceCompare
from functions.pre_check import PreCheck
from functions.snap_data import SnapData
from lib.command_selector import CommandSelector
from functions.compare import compare_flows

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

    before_time, after_time = resource_compare.load(selectors)

    if args.flow:
        # resource_compare.compare_flow()
        before_flow = resource_compare.get_flow(before_time)
        after_flow = resource_compare.get_flow(after_time)
        print compare_flows(before_flow, after_flow)
    elif args.group:
        pass
    elif args.host:
        pass
    elif args.link:
        pass
    elif args.all:
        pass
    else:
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
    group.add_argument('-a', '--all', action='store_true', help='Compare all data.')
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

    # run()

    path = '/Users/wls/.mars_check/1605769167/flows'
    f = open(path, 'r')
    lines = f.readlines()
    ss = ''.join(lines)
    import json
    obj = json.load(ss)
    print obj

    # i = 0
    # l = ['2010-12-31 12:52:30.000','2010-12-31 03:15:30.000', '2010-12-31 22:22:30.000']
    # cmd_selector = CommandSelector(l, 'Please select two time to compare.', 2)
    # selectors = cmd_selector.get_selector()
    # if selectors is not None:
    #     print 'Now compare the value \n    ' + selectors[0] + '\n    ' + selectors[1]


