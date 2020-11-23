# -*- coding:utf-8 -*-

import argparse
import os

from cmd_call import config, snap, pre_check, compare
from constants import DEFAULT_CONFIG_PATH


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

    # device_args = sub_parsers.add_parser('devices', help='Show all the devices info.')
    # device_args.set_defaults(func=show_devices)

    config_args = sub_parsers.add_parser('config', help='Set the mars url/user/password.')
    config_args.add_argument('-u', '--user', help='The mars user name.')
    config_args.add_argument('-p', '--password', help='The mars password.')
    config_args.add_argument('--url', help='The mars host url.(Example: https://192.168.1.20)')
    config_args.set_defaults(func=config)

    snap_args = sub_parsers.add_parser('snap', help='Save the data of now.')
    snap_group = snap_args.add_mutually_exclusive_group(required=True)
    snap_group.add_argument('-l', '--list', action='store_true', help='List all the snap data.')
    snap_group.add_argument('-d', '--delete', action='store_true', help='Delete the select data.')
    snap_group.add_argument('-g', '--get', action='store_true', help='Snap all the data.')
    snap_group.add_argument('-s', '--summary', action='store_true', help='Show the summary of all times.')
    snap_args.set_defaults(func=snap)

    check_args = sub_parsers.add_parser('check', help='Check the flow/group data if correct.')
    check_group = check_args.add_mutually_exclusive_group(required=True)
    check_group.add_argument('-o', '--online', action='store_true', help='Check the online data.')
    check_group.add_argument('-t', '--snap_time', action='store_true', help='Check the data from snap data.')
    check_args.set_defaults(func=pre_check)

    compare_args = sub_parsers.add_parser('compare', help='Compare the different time data.')
    compare_args.add_argument('-d', '--device', help='Specify device for flow or group.')
    group = compare_args.add_mutually_exclusive_group(required=True)
    group.add_argument('-l', '--link', action='store_true', help='Only compare link data.')
    group.add_argument('-f', '--flow', action='store_true', help='Only compare flow data.')
    group.add_argument('-g', '--group', action='store_const', const='all', help='Only compare group data.')
    group.add_argument('-ho', '--host', action='store_true', help='Only compare host data.')
    compare_args.set_defaults(func=compare)

    # argcomplete.autocomplete(parser)
    args = parser.parse_args()
    args.func(args)


def init_config_dir():
    if not os.path.exists(DEFAULT_CONFIG_PATH):
        os.mkdir(DEFAULT_CONFIG_PATH)


if __name__ == '__main__':
    run()
