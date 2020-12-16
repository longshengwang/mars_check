# -*- coding:utf-8 -*-
import os
import sys

from lib.command_single_selector import CommandSingleSelector

file_path = os.path.abspath(__file__)
sys.path.insert(0, os.path.dirname(file_path))

import argparse
import argcomplete as argcomplete
import cmd_call
# import config, snap, pre_check, compare, show_devices, show_links, show_hosts, log
from constants import DEFAULT_CONFIG_PATH


class DeviceIdAction(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        super(DeviceIdAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        print 'values ', values
        setattr(namespace, self.dest, values)


def run():
    init_config_dir()
    parser = argparse.ArgumentParser(description="Mars Check Tool")

    sub_parsers = parser.add_subparsers()

    # config cmd
    config_args = sub_parsers.add_parser('config', help='Set the mars url/user/password.')
    config_args.add_argument('-u', '--user', help='The mars user name.')
    config_args.add_argument('-p', '--password', help='The mars password.')
    config_args.add_argument('--url', help='The mars host url.(Example: https://192.168.1.20)')
    config_args.set_defaults(func=cmd_call.config)

    # show cmd
    show_args = sub_parsers.add_parser('show', help='Show the mars resource.(Devices/Links)')
    show_group = show_args.add_mutually_exclusive_group()

    show_group.add_argument('-o', '--online', action='store_true', help='Show the online data.')
    show_group.add_argument('-s', '--snap_time', action='store_true', help='Show the selected snap data.')
    show_group.add_argument('-l', '--last_snap', action='store_true', help='Show the last snap data.')
    show_group.set_defaults(last_snap=True)

    show_sub_parses = show_args.add_subparsers()

    show_device_args = show_sub_parses.add_parser('device', help='Show devices.')
    show_device_args.set_defaults(func=cmd_call.show_devices)

    show_link_args = show_sub_parses.add_parser('link', help='Show links.')
    show_link_args.set_defaults(func=cmd_call.show_links)

    show_host_args = show_sub_parses.add_parser('host', help='Show hosts.')
    show_host_args.set_defaults(func=cmd_call.show_hosts)

    # snap cmd
    snap_args = sub_parsers.add_parser('snap', help='Save the data of now.')
    snap_group = snap_args.add_mutually_exclusive_group(required=True)
    snap_group.add_argument('-l', '--list', action='store_true', help='List all the snap data.')
    snap_group.add_argument('-d', '--delete', action='store_true', help='Delete the select data.')
    snap_group.add_argument('-g', '--get', action='store_true', help='Snap all the data.')
    snap_group.add_argument('-s', '--summary', action='store_true', help='Show the summary of all times.')
    snap_args.set_defaults(func=cmd_call.snap)

    # check cmd
    check_args = sub_parsers.add_parser('check', help='Check the flow/group data if correct.')
    check_group = check_args.add_mutually_exclusive_group(required=True)
    check_group.add_argument('-o', '--online', action='store_true', help='Check the online data.')
    check_group.add_argument('-s', '--snap_time', action='store_true', help='Check the data from snap data.')
    check_group.add_argument('-l', '--last_snap', action='store_true', help='Check the last snap data.')
    check_args.set_defaults(func=cmd_call.pre_check)

    # compare cmd
    compare_args = sub_parsers.add_parser('compare', help='Compare the different time data.')
    compare_args.add_argument('-d', '--device', help='Specify device for flow or group.')
    group = compare_args.add_mutually_exclusive_group(required=True)
    group.add_argument('-l', '--link', action='store_true', help='Only compare link data.')
    group.add_argument('-f', '--flow', action='store_true', help='Only compare flow data.')
    group.add_argument('-g', '--group', action='store_const', const='all', help='Only compare group data.')
    group.add_argument('-ho', '--host', action='store_true', help='Only compare host data.')
    compare_args.set_defaults(func=cmd_call.compare)

    # trace cmd
    trace_args = sub_parsers.add_parser('trace', help='Trace the path of two hosts.')
    trace_group = trace_args.add_mutually_exclusive_group(required=True)
    trace_group.add_argument('-o', '--online', action='store_true', help='Trace the online data.')
    trace_group.add_argument('-s', '--snap_time', action='store_true', help='Trace the data from snap data.')
    trace_group.add_argument('-l', '--last_snap', action='store_true', help='Trace the last snap data.')
    trace_args.set_defaults(func=cmd_call.trace)

    trace_args.add_argument('-src', required=True, help='The src host ip or mac.')
    trace_args.add_argument('-dst', required=True, help='The dst host ip or mac.')
    trace_args.add_argument('-gw', default=None, help='The gate host ip or mac.(One ip is enough)')

    # log cmd
    log_args = sub_parsers.add_parser('log', help='Show the log with search word.')
    log_args.add_argument('-w', '--word', help='The filter keyword.')
    log_args.add_argument('-l', '--last_hours', type=int, default=2, help='The last hours.(Default is 2)')
    log_args.add_argument('-c', '--count', type=int, default=1000, help='The log count.(Default is 1000)')
    log_args.set_defaults(func=cmd_call.log)

    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    args.func(args)


def init_config_dir():
    if not os.path.exists(DEFAULT_CONFIG_PATH):
        os.mkdir(DEFAULT_CONFIG_PATH)


if __name__ == '__main__':
    run()

    # header_words = ['xxx', 'xxxx1', 'xxxx2']
    # sel = CommandSingleSelector(header_words, 'please select_one')
    # print sel.get_selector()
