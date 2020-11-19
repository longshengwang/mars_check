# -*- coding:utf-8 -*-
import re
import time
import json

import requests
from requests.auth import HTTPBasicAuth

from constants import ETH_TYPE_CODE, DEVICE_CONFIG_NAME, DEVICE_NAME, FLOW_NAME, GROUPS_NAME, \
    HOSTS_NAME, LINKS_NAME


def get(url, auth):
    res = requests.get(url, auth=HTTPBasicAuth(auth['user_name'], auth['password']), verify=False)
    if res.status_code == 200:
        return res.json()


def flow_to_line_string(flow, host_object, device_config_object):
    end = ' ; '
    res = '[ FLOW ] state=>' + flow['state'] + '; Device=>'
    device_id = flow['deviceId']
    device_name = device_config_object.get_device_name(device_id)
    if device_name is None:
        device_name = device_id

    res = res + device_name + end
    if flow['selector'] and flow['selector']['criteria'] and len(flow['selector']['criteria']) > 0:
        criteria = flow['selector']['criteria']
        res = res + 'SELECTOR=>'
        for item in criteria:
            if item['type'] == 'ETH_SRC':
                mac = item['mac']
                res = res + 'ETH_SRC:' + mac
                ip = host_object.get_ip(mac)
                if ip:
                    res = res + '(' + ip + ')'
                res += ','
            elif item['type'] == 'ETH_DST':
                mac = item['mac']
                res = res + 'ETH_DST:' + mac
                ip = host_object.get_ip(mac)
                if ip:
                    res = res + '(' + ip + ')'
                res += ','
            elif item['type'] == 'ETH_TYPE':
                eth_type_word = ETH_TYPE_CODE.get(item['ethType'])
                res = res + 'ETH_TYPE:' + eth_type_word + ','
            else:
                keys = item.keys()
                keys.remove('type')
                res = res + ' ' + item['type'] + ':' + str(item[keys[0]]) + ','
        res = remove_last_word(res)
        res += end

    if flow['treatment'] and flow['treatment']['instructions']:
        instructions = flow['treatment']['instructions']
        res = res + "ACTION=>"
        for item in instructions:
            keys = item.keys()
            keys.remove('type')
            value = item[keys[0]]
            res = res + item['type'] + ':' + value
            if item['type'] == 'GROUP':
                r = re.findall(r'0x1(.+?)}', value)
                if len(r) > 0:
                    port = int(r[0], 16)
                    res = res + '(' + str(port) + ')'
            res += ','
        res = remove_last_word(res)
        res += ';'

    if flow['treatment'] and flow['treatment']['deferred']:
        deffers = flow['treatment']['deferred']
        res = res + "ACTION=>"
        for item in deffers:
            keys = item.keys()
            keys.remove('type')
            value = item[keys[0]]

            if item['type'] == 'GROUP':
                res = res + item['type'] + ':'
                r = re.findall(r'0x1(.+?)}', value)
                if len(r) > 0:
                    res = res + '0x1' + r[0]
                    port = int(r[0], 16)
                    res = res + '(portId:' + str(port) + ')'
            else:
                res = res + item['type'] + ':' + value
            res += ','
        res = remove_last_word(res)
        res += ';'
    return res


def group_to_line_string(group, device_config_object):
    end = ' ; '
    res = '[ GROUP ] GroupId=>' + hex(int(group['id'])) + '; state=>' + group['state'] + '; Device=>'
    device_id = group['deviceId']
    device_name = device_config_object.get_device_name(device_id)
    if device_name is None:
        device_name = device_id

    res = res + device_name + end
    if group['buckets']:
        buckets = group['buckets']
        for index, bucket in enumerate(buckets, start=1):
            treatment = bucket['treatment']
            res = res + 'BUCKET[' + str(index) + ']=>{ '
            # res = res + json.dumps(treatment) + ';'
            if treatment['instructions'] and len(treatment['instructions']) > 0:
                instructions = treatment['instructions']
                res = res + 'INSTRUCTION=>{ '
                for instruction in instructions:
                    keys = instruction.keys()
                    keys.remove('type')
                    in_type = instruction['type']
                    value = instruction[keys[0]]
                    res = res + in_type + ':' + value + ','
                res = remove_last_word(res)
                res = res + ' };'

            if treatment['deferred'] and len(treatment['deferred']) > 0:
                deferred = treatment['deferred']
                res = res + 'DEFERRED=>{ '
                for defer in deferred:
                    keys = defer.keys()
                    keys.remove('type')
                    in_type = defer['type']
                    value = defer[keys[0]]
                    res = res + in_type + ':' + value + ','
                res = remove_last_word(res)
                res = res + ' };'
            res += ' };'
    return res


def host_to_line_string(host, device_config_obj):
    host_location_list = []
    for location in host['locations']:
        host_location_list.append(
            device_config_obj.get_device_name(location['elementId']) + '/' + location['port'])

    res = '[ HOST ] MAC: ' + host['mac'] + '; LOCATION: ' + ','.join(host_location_list) + '; '

    if 'lastUpdateTime' in host:
        res = res + 'LAST_UPDATE: ' + format_time_stamp_2_string(host['lastUpdateTime']) + '; '

    if host['ipAddresses'] is not None and len(host['ipAddresses']) > 0:
        res = res + 'IP_ADDRESS:' + ','.join(host['ipAddresses']) + '; '

    return res


def link_to_line_string(link, device_config_obj):
    src = link['src']
    dst = link['dst']

    one = device_config_obj.get_device_name(src['device']) + '/' + src['port']
    two = device_config_obj.get_device_name(dst['device']) + '/' + dst['port']

    res = '[ LINK ] ' + one + ' <==> ' + two + '; TYPE: ' + link['type'] + '; STATE: ' + link['state'] + ';'
    return res


def remove_last_word(word):
    return word[0:-1]


def format_time_stamp_2_string(time_stamp_str, is_mill=True):
    time_stamp = int(time_stamp_str)
    if is_mill:
        time_stamp = time_stamp / 1000
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time_stamp))


def get_flow(mars_config, snap_time):
    flow_str = _get_data_from_snap(mars_config, snap_time, FLOW_NAME)
    return json.loads(flow_str)


def get_devices(mars_config, snap_time):
    devices_str = _get_data_from_snap(mars_config, snap_time, DEVICE_NAME)
    return json.loads(devices_str)


def get_devices_configs(mars_config, snap_time):
    devices_config_str = _get_data_from_snap(mars_config, snap_time, DEVICE_CONFIG_NAME)
    return json.loads(devices_config_str)


def get_group(mars_config, snap_time):
    group_str = _get_data_from_snap(mars_config, snap_time, GROUPS_NAME)
    return json.loads(group_str)


def get_link(mars_config, snap_time):
    link_str = _get_data_from_snap(mars_config, snap_time, LINKS_NAME)
    return json.loads(link_str)


def get_host(mars_config, snap_time):
    host_str = _get_data_from_snap(mars_config, snap_time, HOSTS_NAME)
    return json.loads(host_str)


def _get_data_from_snap(mars_config, snap_time, words):
    path_dir = mars_config.get_base_path()
    file_path = path_dir + snap_time + '/' + words
    f = open(file_path, 'r')
    lines = f.readlines()
    data_str = ''.join(lines)
    f.close()
    return data_str


def fix_string_to_size(word, n):
    return (n - len(word)) * ' ' + word
