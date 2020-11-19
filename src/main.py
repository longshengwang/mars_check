# -*- coding:utf-8 -*-

import argparse
import os
from os.path import expanduser

from config import MarsConfig
from functions.compare import ResourceCompare
from functions.compare import compare_flows, compare_groups, compare_hosts, compare_link
from functions.pre_check import PreCheck
from functions.snap_data import SnapData
from lib.color import UseStyle
from lib.command_selector import CommandSelector
from lib.printer import print_normal, print_normal_center, print_normal_end, print_normal_start, \
    print_normal_sub
from utils import flow_to_line_string, group_to_line_string, host_to_line_string, link_to_line_string

DEFAULT_CONFIG_PATH = expanduser("~") + '/.mars_check/'
MAX_BACKUP_COUNT = 20

URL_CONFIG_FILE = '.url'
USER_CONFIG_FILE = '.user'
PASSWORD_CONFIG_FILE = '.password'


def read_config(path):
    f = open(path)
    line = f.readline()
    f.close()
    return line.rstrip()


def write_config(path, content):
    f = open(path, 'w+')
    f.write(content)
    f.close()


def get_mars_config():
    files = os.listdir(DEFAULT_CONFIG_PATH)
    url = 'https://127.0.0.1'
    user = 'karaf'
    password = 'karaf'
    if URL_CONFIG_FILE in files:
        res = read_config(DEFAULT_CONFIG_PATH + URL_CONFIG_FILE)
        if res != '':
            url = res

    if USER_CONFIG_FILE in files:
        res = read_config(DEFAULT_CONFIG_PATH + USER_CONFIG_FILE)
        if res != '':
            user = res

    if PASSWORD_CONFIG_FILE in files:
        res = read_config(DEFAULT_CONFIG_PATH + PASSWORD_CONFIG_FILE)
        if res != '':
            password = res
    return MarsConfig(url, user, password, DEFAULT_CONFIG_PATH)


def config(args):
    if args.user is not None:
        write_config(DEFAULT_CONFIG_PATH + USER_CONFIG_FILE, args.user)

    if args.password is not None:
        write_config(DEFAULT_CONFIG_PATH + PASSWORD_CONFIG_FILE, args.password)

    if args.url is not None:
        write_config(DEFAULT_CONFIG_PATH + URL_CONFIG_FILE, args.url)


def snap(args):
    mars_config = get_mars_config()
    snap = SnapData(mars_config)
    if args.list:
        resource_compare = ResourceCompare(mars_config)
        snap_times = resource_compare.get_all_snap_time()
        for item in snap_times:
            print item
        return

    snap.snap_all_data()


def compare(args):
    mars_config = get_mars_config()
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
            print_normal_sub('--- Added')
            changes_json = res[key]
            if len(changes_json['added']) > 0:
                for item in changes_json['added']:
                    print_normal_center(
                        flow_to_line_string(item, resource_compare.host_object, resource_compare.device_config_object),
                        'green')

            print_normal_sub('--- Removed')
            if changes_json['removed'] and len(changes_json['removed']) > 0:
                for item in changes_json['removed']:
                    print_normal_center(
                        flow_to_line_string(item, resource_compare.host_object, resource_compare.device_config_object),
                        'red')

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
            print_normal_sub('--- Added')
            changes_json = res[key]
            if len(changes_json['added']) > 0:
                for item in changes_json['added']:
                    print_normal_center(group_to_line_string(item, resource_compare.device_config_object), 'green')

            # print_normal(UseStyle('Device Name: ' + device_name + ' ====> Removed', fore='yellow'))
            print_normal_sub('--- Removed')
            if changes_json['removed'] and len(changes_json['removed']) > 0:
                for item in changes_json['removed']:
                    print_normal_center(group_to_line_string(item, resource_compare.device_config_object), 'red')
            print_normal_end('')
            print_normal('')
    elif args.host:
        print_normal('====  HOST COMPARE ====')
        before_host = resource_compare.get_host(before_time)
        after_host = resource_compare.get_host(after_time)
        res = compare_hosts(before_host, after_host, resource_compare.device_config_object)

        print_normal_start('')
        print_normal_sub('--- Added')
        if len(res['added']) > 0:
            for item in res['added']:
                print_normal_center(host_to_line_string(item, resource_compare.device_config_object), 'green')

        # print_normal(UseStyle('Device Name: ' + device_name + ' ====> Removed', fore='yellow'))
        print_normal_sub('--- Removed')
        if res['removed'] and len(res['removed']) > 0:
            for item in res['removed']:
                print_normal_center(host_to_line_string(item, resource_compare.device_config_object), 'red')

        print_normal_sub('--- Modified')
        if res['modified'] and len(res['modified']) > 0:
            for item in res['modified']:
                print_normal_center(str(item), 'cyan')
        print_normal_end('')
        print_normal('')
    elif args.link:
        print_normal('====  LINK COMPARE ====')
        before_link = resource_compare.get_link(before_time)
        after_link = resource_compare.get_link(after_time)
        res = compare_link(before_link, after_link)
        #  resource_compare.device_config_object)

        print_normal_start('')
        print_normal_sub('--- Added')
        if len(res['added']) > 0:
            for item in res['added']:
                print_normal_center(link_to_line_string(item, resource_compare.device_config_object), 'green')

        # print_normal(UseStyle('Device Name: ' + device_name + ' ====> Removed', fore='yellow'))
        print_normal_sub('--- Removed')
        if res['removed'] and len(res['removed']) > 0:
            for item in res['removed']:
                print_normal_center(link_to_line_string(item, resource_compare.device_config_object), 'red')
        print_normal_end('')
        print_normal('')


def pre_check(args):
    mars_config = get_mars_config()
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

    config_args = sub_parsers.add_parser('config', help='Set the mars url/user/password.')
    config_args.add_argument('-u', '--user', help='The mars user name.')
    config_args.add_argument('-p', '--password', help='The mars password.')
    config_args.add_argument('--url', help='The mars host url.(Example: https://192.168.1.20)')
    config_args.set_defaults(func=config)

    snap_args = sub_parsers.add_parser('snap', help='Save the data of now.')
    snap_group = snap_args.add_mutually_exclusive_group()
    snap_group.add_argument('-l', '--list', action='store_true', help='List all the snap data.')
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
    compare_args.set_defaults(func=compare)

    # argcomplete.autocomplete(parser)
    args = parser.parse_args()
    args.func(args)


def init_config_dir():
    if not os.path.exists(DEFAULT_CONFIG_PATH):
        os.mkdir(DEFAULT_CONFIG_PATH)


if __name__ == '__main__':
    run()
