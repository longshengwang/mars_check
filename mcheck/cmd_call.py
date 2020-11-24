# -*- coding:utf8 -*-
import os

from os.path import expanduser

from config import MarsConfig
from functions.compare import ResourceCompare
from functions.compare import compare_flows, compare_groups, compare_hosts, compare_link
from functions.log import Log
from functions.check import Check
from functions.show import ShowResource
from functions.snap_data import SnapData
from lib.color import UseStyle
from lib.command_selector import CommandSelector
from lib.printer import print_normal, print_normal_center, print_normal_end, print_normal_start, \
    print_normal_sub
from utils import flow_to_line_string, group_to_line_string, host_to_line_string, link_to_line_string
from utils import get_flow, get_group, get_host, get_link
from utils import fix_string_to_size, get_all_snap_time
from constants import DEVICE_NAME, DEVICE_CONFIG_NAME, LINKS_NAME, HOSTS_NAME, FLOW_NAME, GROUPS_NAME
from constants import DEFAULT_CONFIG_PATH, URL_CONFIG_FILE, USER_CONFIG_FILE, PASSWORD_CONFIG_FILE


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

    if args.url is None and args.password is None and args.user is None:
        mars_config = get_mars_config()
        print UseStyle("Mars Check Config", fore='green')
        print UseStyle(' |-- URL  : ', fore='green') + mars_config.get_url()
        print UseStyle(' |-- USER : ', fore='green') + mars_config.get_auth()['user_name']


def snap(args):
    mars_config = get_mars_config()
    snap_obj = SnapData(mars_config)
    if args.list:
        snap_times = get_all_snap_time(mars_config)
        for item in snap_times:
            print item
    elif args.get:
        snap_obj.snap_all_data()
    elif args.summary:
        for item in snap_obj.get_summary():
            res = item['time'] + UseStyle(' | ', fore='red')
            word_len = 4

            res = res + FLOW_NAME + ':' + fix_string_to_size(str(item[FLOW_NAME]), word_len) \
                  + UseStyle(' | ', fore='red')
            res = res + GROUPS_NAME + ':' + fix_string_to_size(str(item[GROUPS_NAME]), word_len) \
                  + UseStyle(' | ', fore='red')
            res = res + DEVICE_NAME + ':' + fix_string_to_size(str(item[DEVICE_NAME]), word_len) \
                  + UseStyle(' | ', fore='red')
            res = res + DEVICE_CONFIG_NAME + ':' + fix_string_to_size(str(item[DEVICE_CONFIG_NAME]), word_len) \
                  + UseStyle(' | ', fore='red')
            res = res + HOSTS_NAME + ':' + fix_string_to_size(str(item[HOSTS_NAME]), word_len) \
                  + UseStyle(' | ', fore='red')
            res = res + LINKS_NAME + ':' + fix_string_to_size(str(item[LINKS_NAME]), word_len)

            print res
    elif args.delete:
        snap_times = get_all_snap_time(mars_config)
        cmd_selector = CommandSelector(snap_times, 'Please select times to delete.')
        selectors = cmd_selector.get_selector()
        if len(selectors) == 0:
            print 'No data is selected for delete.'
            return
        else:
            user_input = raw_input('Are you sure to ' + UseStyle('delete', fore='red') + ' the data: '
                                   + UseStyle(', '.join(selectors), fore='red') + ' ?(Y/N):')

            if user_input == 'y' or user_input == 'Y' or user_input == 'yes' or user_input == 'YES':
                snap_obj.delete(selectors)


def compare(args):
    mars_config = get_mars_config()
    resource_compare = ResourceCompare(mars_config)
    snap_times = get_all_snap_time(mars_config)
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
        before_flow = get_flow(mars_config, before_time)
        after_flow = get_flow(mars_config, after_time)
        res = compare_flows(before_flow, after_flow)
        keys = res.keys()
        for key in keys:
            device_name = resource_compare.device_config_object.get_device_name(key)
            if args.device is not None and (device_name != args.device and device_name != args.device):
                continue

            changes_json = res[key]
            print_normal(UseStyle('Device Name: ' + device_name, fore='yellow'))
            # print_normal(UseStyle('Device Name: ' + device_name + ' ====> Added', fore='yellow'))
            print_normal_start('')
            print_normal_sub('--- Added(' + str(len(changes_json['added'])) + ')')
            if len(changes_json['added']) > 0:
                for item in changes_json['added']:
                    print_normal_center(
                        flow_to_line_string(item, resource_compare.host_object, resource_compare.device_config_object),
                        'green')

            print_normal_sub('--- Removed(' + str(len(changes_json['removed'])) + ')')
            if changes_json['removed'] and len(changes_json['removed']) > 0:
                for item in changes_json['removed']:
                    print_normal_center(
                        flow_to_line_string(item, resource_compare.host_object, resource_compare.device_config_object),
                        'red')

            print_normal_end('')
            print_normal('')
    elif args.group:
        print_normal('====  GROUPS COMPARE ====')
        before_group = get_group(mars_config, before_time)
        after_group = get_group(mars_config, after_time)
        res = compare_groups(before_group, after_group)
        keys = res.keys()
        for key in keys:
            device_name = resource_compare.device_config_object.get_device_name(key)
            if args.device is not None and (device_name != args.device and device_name != args.device):
                continue

            changes_json = res[key]
            print_normal(UseStyle('Device Name: ' + device_name, fore='yellow'))
            # print_normal(UseStyle('Device Name: ' + device_name + ' ====> Added', fore='yellow'))
            print_normal_start('')
            print_normal_sub('--- Added(' + str(len(changes_json['added'])) + ')')

            if len(changes_json['added']) > 0:
                for item in changes_json['added']:
                    print_normal_center(group_to_line_string(item, resource_compare.device_config_object), 'green')

            # print_normal(UseStyle('Device Name: ' + device_name + ' ====> Removed', fore='yellow'))
            print_normal_sub('--- Removed(' + str(len(changes_json['removed'])) + ')')
            if changes_json['removed'] and len(changes_json['removed']) > 0:
                for item in changes_json['removed']:
                    print_normal_center(group_to_line_string(item, resource_compare.device_config_object), 'red')
            print_normal_end('')
            print_normal('')
    elif args.host:
        print_normal('====  HOST COMPARE ====')
        before_host = get_host(mars_config, before_time)
        after_host = get_host(mars_config, after_time)
        res = compare_hosts(before_host, after_host, resource_compare.device_config_object)

        print_normal_start('')
        print_normal_sub('--- Added(' + str(len(res['added'])) + ')')
        if len(res['added']) > 0:
            for item in res['added']:
                print_normal_center(host_to_line_string(item, resource_compare.device_config_object), 'green')

        # print_normal(UseStyle('Device Name: ' + device_name + ' ====> Removed', fore='yellow'))
        print_normal_sub('--- Removed(' + str(len(res['removed'])) + ')')
        if res['removed'] and len(res['removed']) > 0:
            for item in res['removed']:
                print_normal_center(host_to_line_string(item, resource_compare.device_config_object), 'red')

        print_normal_sub('--- Modified(' + str(len(res['modified'])) + ')')
        if res['modified'] and len(res['modified']) > 0:
            for item in res['modified']:
                print_normal_center(str(item), 'cyan')
        print_normal_end('')
        print_normal('')
    elif args.link:
        print_normal('====  LINK COMPARE ====')
        before_link = get_link(mars_config, before_time)
        after_link = get_link(mars_config, after_time)
        res = compare_link(before_link, after_link)
        #  resource_compare.device_config_object)

        print_normal_start('')
        print_normal_sub('--- Added(' + str(len(res['added'])) + ')')
        if len(res['added']) > 0:
            for item in res['added']:
                print_normal_center(link_to_line_string(item, resource_compare.device_config_object), 'green')

        # print_normal(UseStyle('Device Name: ' + device_name + ' ====> Removed', fore='yellow'))
        print_normal_sub('--- Removed(' + str(len(res['removed'])) + ')')
        if res['removed'] and len(res['removed']) > 0:
            for item in res['removed']:
                print_normal_center(link_to_line_string(item, resource_compare.device_config_object), 'red')
        print_normal_end('')
        print_normal('')


def pre_check(args):
    mars_config = get_mars_config()
    if args.online:
        check = Check(mars_config)
        check.check_online()
    elif args.snap_time:
        snap_times = get_all_snap_time(mars_config)
        cmd_selector = CommandSelector(snap_times, 'Please select one time to check.', select_count=1)
        selectors = cmd_selector.get_selector()
        if selectors is None:
            print 'No data is selected for check.'
        elif len(selectors) > 1:
            pass
        else:
            check = Check(mars_config)
            check.check_snap(selectors[0])
    elif args.last_snap:
        snap_times = get_all_snap_time(mars_config)
        if len(snap_times) > 0:
            check = Check(mars_config)
            check.check_snap(snap_times[0])


def show_devices(args):
    mars_config = get_mars_config()
    if args.online:
        show_obj = ShowResource(mars_config)
        show_obj.show_online_devices()
    elif args.snap_time:
        snap_times = get_all_snap_time(mars_config)
        cmd_selector = CommandSelector(snap_times, 'Please select one time to show.', select_count=1)
        selectors = cmd_selector.get_selector()
        if selectors is None:
            print 'No data is selected for show.'
        elif len(selectors) > 1:
            pass
        else:
            show_obj = ShowResource(mars_config)
            show_obj.show_snap_devices(selectors[0])
    elif args.last_snap:
        snap_times = get_all_snap_time(mars_config)
        if len(snap_times) > 0:
            show_obj = ShowResource(mars_config)
            show_obj.show_snap_devices(snap_times[0])


def show_links(args):
    mars_config = get_mars_config()
    if args.online:
        show_obj = ShowResource(mars_config)
        show_obj.show_online_links()
    elif args.snap_time:
        snap_times = get_all_snap_time(mars_config)
        cmd_selector = CommandSelector(snap_times, 'Please select one time to show.', select_count=1)
        selectors = cmd_selector.get_selector()
        if selectors is None:
            print 'No data is selected for show.'
        elif len(selectors) > 1:
            pass
        else:
            show_obj = ShowResource(mars_config)
            show_obj.show_snap_links(selectors[0])
    elif args.last_snap:
        snap_times = get_all_snap_time(mars_config)
        if len(snap_times) > 0:
            show_obj = ShowResource(mars_config)
            show_obj.show_snap_links(snap_times[0])


def show_hosts(args):
    mars_config = get_mars_config()
    if args.online:
        show_obj = ShowResource(mars_config)
        show_obj.show_online_hosts()
    elif args.snap_time:
        snap_times = get_all_snap_time(mars_config)
        cmd_selector = CommandSelector(snap_times, 'Please select one time to show.', select_count=1)
        selectors = cmd_selector.get_selector()
        if selectors is None:
            print 'No data is selected for show.'
        elif len(selectors) > 1:
            pass
        else:
            show_obj = ShowResource(mars_config)
            show_obj.show_snap_hosts(selectors[0])
    elif args.last_snap:
        snap_times = get_all_snap_time(mars_config)
        if len(snap_times) > 0:
            show_obj = ShowResource(mars_config)
            show_obj.show_snap_hosts(snap_times[0])


def log(args):
    mars_config = get_mars_config()
    word = ''
    if args.word is not None:
        word = args.word

    log = Log(mars_config)
    log.show(word, args.count, args.last_hours)
