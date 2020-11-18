# -*- coding:utf8 -*-

import os
import argparse
from os.path import expanduser

from config import MarsConfig
from functions.pre_check import PreCheck
from functions.snap_data import SnapData

DEFAULT_CONFIG_PATH = '/.mars_check/'
MAX_BACKUP_COUNT = 20


def snap(args):
    mars_config = MarsConfig("https://210.63.204.28", 'karaf', 'karaf', expanduser("~") + DEFAULT_CONFIG_PATH)
    snap = SnapData(mars_config)
    snap.snap_all_data()


def compare(args):
    print args.flow
    print args.all
    print args.host
    print args.group
    print 'compare'


def pre_check(args):
    mars_config = MarsConfig("https://210.63.204.28", 'karaf', 'karaf', expanduser("~") + DEFAULT_CONFIG_PATH)
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
    # run()
    # -*- coding:utf8 -*-
    import time, sys


    def progressbar():
        print 'Loading...'
        print "[+] start to build...."
        height = 4
        for i in range(0, 100):
            if i > 0:
                sys.stdout.write(u'\u001b[1A')
            time.sleep(0.1)
            width = (i + 1) / 4
            bar = '[' + '#' * width + ' ' * (25 - width) + ']'
            sys.stdout.write(u'\u001b[1000D\u001b[2K' + ' | -> ' + bar + '\n')
            sys.stdout.write(u'\u001b[1000D\u001b[2K' + ' | -> ' + bar)
            sys.stdout.flush()

        sys.stdout.write(u'\u001b[1A')
        sys.stdout.write(u'\u001b[1A')
        sys.stdout.write(u'\u001b[1000D')
        sys.stdout.write(u'\u001b[J')
        sys.stdout.write('[-] Finish build')
        sys.stdout.flush()
        print


    progressbar()

