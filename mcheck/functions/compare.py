# -*- coding:utf-8 -*-
import json
import time

from resource import DeviceConfigs, Hosts
from utils import format_time_stamp_2_string


class ResourceCompare:
    mars_config = None
    device_config_object = None
    flow_object = None
    group_object = None
    host_object = None

    def __init__(self, mars_config):
        self.mars_config = mars_config

    def _load_device_config(self, after_time):
        path_dir = self.mars_config.get_base_path()
        device_path = path_dir + after_time + '/devices_config'

        f = open(device_path, 'r')
        lines = f.readlines()
        device_config_str = ''.join(lines)
        f.close()
        self.device_config_object = DeviceConfigs.initialize_with(self.mars_config, json.loads(device_config_str))

    def _load_hosts(self, after_time):
        path_dir = self.mars_config.get_base_path()
        hosts_path = path_dir + after_time + '/hosts'

        f = open(hosts_path, 'r')
        lines = f.readlines()
        host_str = ''.join(lines)
        f.close()
        self.host_object = Hosts.initialize_with(self.mars_config, json.loads(host_str))

    def load(self, compared_times):
        parsed_times = [str(int(time.mktime(time.strptime(i, '%Y-%m-%d %H:%M:%S')))) for i in compared_times]
        parsed_times.sort()
        before_time = parsed_times[0]
        after_time = parsed_times[1]

        self._load_device_config(after_time)
        self._load_hosts(after_time)

        return str(before_time), str(after_time)


# -----------------------------

def compare_hosts(before_hosts, after_hosts, device_config_obj):
    modify_host_str_list = []
    new_hosts = []

    before_host_dict = {}
    for item in before_hosts:
        before_host_dict[item['mac']] = item

    for item in after_hosts:
        mac = item['mac']
        if mac in before_host_dict:
            before_host = before_host_dict[item['mac']]
            res = _compare_host(before_host, item, device_config_obj)
            if res is not None:
                modify_host_str_list.append(res)
            del before_host_dict[mac]
        else:
            new_hosts.append(item)
    return {'added': new_hosts, 'removed': before_host_dict.values(), 'modified': modify_host_str_list}


def compare_flows(before_flows, after_flows, device_id_4_compare=None):
    res = {}
    before_flows_dict = {}
    for item in before_flows:
        before_flows_dict[item['id']] = item

    for item in after_flows:
        _id = item['id']
        device_id = item['deviceId']
        if device_id_4_compare is not None and device_id_4_compare != device_id:
            continue

        if _id in before_flows_dict:
            del before_flows_dict[_id]
        else:
            if device_id not in res:
                res[device_id] = {'added': [], 'removed': []}
            res[device_id]['added'].append(item)

    for item in before_flows_dict.values():
        device_id = item['deviceId']

        if device_id_4_compare is not None and device_id_4_compare != device_id:
            continue

        if device_id not in res:
            res[device_id] = {'added': [], 'removed': []}
        res[device_id]['removed'].append(item)
    return res


def compare_groups(before_groups, after_groups, device_id_4_compare=None):
    res = {}
    before_groups_dict = {}
    for item in before_groups:
        g_id = item['id']
        device_id = item['deviceId']
        before_groups_dict[device_id + '/' + g_id] = item

    for item in after_groups:
        g_id = item['id']
        device_id = item['deviceId']
        if device_id_4_compare is not None and device_id_4_compare != device_id:
            continue

        if device_id + '/' + g_id in before_groups_dict:
            del before_groups_dict[device_id + '/' + g_id]
        else:
            if device_id not in res:
                res[device_id] = {'added': [], 'removed': []}
            res[device_id]['added'].append(item)

    for item in before_groups_dict.values():
        device_id = item['deviceId']
        if device_id_4_compare is not None and device_id_4_compare != device_id:
            continue
        if device_id not in res:
            res[device_id] = {'added': [], 'removed': []}
        res[device_id]['removed'].append(item)
    return res


'''
{
    "dst": {
        "device": "of:0000b86a970c01c0",
        "port": "47"
    },
    "src": {
        "device": "of:0000b86a97145100",
        "port": "23"
    },
    "state": "ACTIVE",
    "type": "INDIRECT"
},
'''


def compare_link(before_links, after_links):
    res = {'added': [], 'removed': []}
    before_links_dict = {}
    after_links_dict = {}
    for item in before_links:
        link_id = _get_link_id(item)
        if link_id not in before_links_dict:
            before_links_dict[link_id] = item

    for item in after_links:
        a_link_id = _get_link_id(item)
        if a_link_id not in after_links_dict:
            after_links_dict[a_link_id] = item

    for link_id in after_links_dict:
        if link_id in before_links_dict:
            del before_links_dict[link_id]
        else:
            res['added'].append(after_links_dict[link_id])

    for item in before_links_dict.values():
        res['removed'].append(item)

    return res


def _get_link_id(link):
    src_word = link['src']['device'] + '/' + link['src']['port']
    dst_word = link['dst']['device'] + '/' + link['dst']['port']
    if src_word > dst_word:
        return dst_word + '_' + src_word
    else:
        return src_word + '_' + dst_word


# def _get_data(self):
#     self.device_config_object = devices.DeviceConfigs.initialize(self.mars_config)
#     self.flow_object = flows.Flows.initialize(self.mars_config)
#     self.group_object = flows.Groups.initialize(self.mars_config)
#     self.host_object = hosts.Hosts.initialize(self.mars_config)
def _compare_host(before_host, after_host, device_config_obj):
    res = ''

    before_host['ipAddresses'].sort()
    after_host['ipAddresses'].sort()
    before_host_ip_str = ','.join(before_host['ipAddresses'])
    after_host_ip_str = ','.join(after_host['ipAddresses'])

    before_host_location_list = []
    for location in before_host['locations']:
        before_host_location_list.append(
            device_config_obj.get_device_name(location['elementId']) + '/' + location['port'])

    before_host_location_list.sort()
    before_host_location_str = ','.join(before_host_location_list)

    after_host_location_list = []
    for location in after_host['locations']:
        after_host_location_list.append(
            device_config_obj.get_device_name(location['elementId']) + '/' + location['port'])

    after_host_location_list.sort()
    after_host_location_str = ','.join(after_host_location_list)

    if before_host_ip_str != after_host_ip_str:
        res = res + ' IP_ADDRESS: ' + before_host_ip_str + ' => ' + after_host_ip_str + ';'
    if before_host_location_str != after_host_location_str:
        res = res + ' LOCATION:  ' + before_host_location_str + ' => ' + after_host_location_str + ';'

    if 'lastUpdateTime' in before_host:
        before_host_last_update = before_host['lastUpdateTime']
        after_host_last_update = after_host['lastUpdateTime']
        if before_host_last_update != after_host_last_update:
            res = res + ' LAST_UPDATE:' + format_time_stamp_2_string(before_host_last_update) + ' => ' \
                  + format_time_stamp_2_string(after_host_last_update) + ';'

    if res == '':
        return None

    return '[ HOST ] Host: ' + before_host['mac'] + '   ' + res
