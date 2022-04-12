# -*- coding:utf8 -*-
import re

from lib.color import UseStyle
from utils import flow_to_line_string


def find_path(flows, links, groups, src_host, dst_host):
    src_mac = src_host['mac']
    dst_mac = dst_host['mac']

    filter_flow_models = find_flows(flows, src_mac, dst_mac)

    if len(filter_flow_models) == 0:
        raise Exception('No flow found.')

    parse_flows_output(filter_flow_models, groups)

    link_manage = LinkManager(links)
    paths = find_order_path(filter_flow_models, link_manage)
    return paths
    # except Exception, e:
    #     print e.message
    #     raise e


# return the flow models
def find_flows(flows, src_mac, dst_mac):
    filter_flows = []
    for flow in flows:
        flow_model = FlowModel(flow, src_mac, dst_mac)
        if flow_model.parse():
            filter_flows.append(flow_model)
    return filter_flows


# make all the flow models parse the output port from groups
def parse_flows_output(flow_models, groups):
    for flow_model in flow_models:
        flow_model.parse_output_port(groups)


def find_order_path(flow_models, link_manager):
    in_degree = {}
    device_flow_models_dict = {}

    for flow_model in flow_models:
        device_id = flow_model.flow['deviceId']
        src_port = flow_model.in_port
        out_port = flow_model.out_port

        input_key = device_id + '/' + src_port

        if input_key not in device_flow_models_dict:
            device_flow_models_dict[input_key] = flow_model
        else:
            raise Exception('Something error with multi flow with same in port at device: ' + input_key)

        if input_key not in in_degree:
            in_degree[input_key] = 0

        output_key = device_id + '/' + out_port
        dst = link_manager.get_dst(output_key)
        if dst is not None:
            target_key = dst['device'] + '/' + dst['port']
            if dst['device'] not in in_degree:
                in_degree[target_key] = 1
            else:
                in_degree[target_key] = in_degree[target_key] + 1

    source_locations = [input_key for input_key in in_degree if in_degree[input_key] == 0]

    if len(source_locations) == 1:
        paths = []
        source_loc = source_locations[0]
        source_flow_model = device_flow_models_dict[source_loc]
        paths.append(source_flow_model)

        while source_flow_model is not None:
            out_loc = source_flow_model.flow['deviceId'] + '/' + source_flow_model.out_port
            dst = link_manager.get_dst(out_loc)
            if dst is not None:
                target_key = dst['device'] + '/' + dst['port']
                if device_flow_models_dict.has_key(target_key):
                    source_flow_model = device_flow_models_dict.get(target_key)
                    source_loc = target_key
                    paths.append(source_flow_model)
                else:
                    break
            else:
                break
        return paths
    elif len(source_locations) > 1:
        raise Exception('It seems has multi source : ' + ','.join(source_locations))
    else:
        raise Exception('No source can be found :' + str(in_degree))


def find_output_port(flow, groups):
    group_id_in_flow = get_flow_group_id(flow)
    for group in groups:
        if group['deviceId'] == flow['deviceId']:
            group_id_str = hex(int(group['id']))
            if group_id_in_flow is not None:
                if group_id_in_flow == group_id_str:
                    return get_group_output_port(group)
    return None


def get_group_output_port(group):
    if group['buckets']:
        buckets = group['buckets']
        for index, bucket in enumerate(buckets, start=1):
            treatment = bucket['treatment']
            if treatment['instructions'] and len(treatment['instructions']) > 0:
                instructions = treatment['instructions']
                for instruction in instructions:
                    if instruction['type'] == 'OUTPUT' and instruction.has_key('port'):
                        return instruction.get('port')

            if treatment['deferred'] and len(treatment['deferred']) > 0:
                deferred = treatment['deferred']
                for defer in deferred:
                    if defer['type'] == 'OUTPUT' and defer.has_key('port'):
                        return defer.get('port')
    return None


def get_flow_group_id(flow):
    if flow['treatment'] and flow['treatment']['instructions']:
        instructions = flow['treatment']['instructions']
        for item in instructions:
            keys = item.keys()
            keys.remove('type')
            value = item[keys[0]]
            if item['type'] == 'GROUP':
                r = re.findall(r'{id=(.+?)}', value)
                if len(r) > 0:
                    return r[0]
    return None


class FlowModel:
    flow = None
    src_mac = None
    dst_mac = None
    in_port = None  # string
    group_id = None  # string
    out_port = None  # string

    def __init__(self, flow, src_mac, dst_mac):
        self.flow = flow
        self.src_mac = src_mac
        self.dst_mac = dst_mac

    def parse(self):
        is_src_same = False
        is_dst_same = False
        if self.flow['selector'] and self.flow['selector']['criteria'] and len(self.flow['selector']['criteria']) > 0:
            criteria = self.flow['selector']['criteria']
            for item in criteria:
                if item['type'] == 'ETH_SRC':
                    if item['mac'] == self.src_mac:
                        is_src_same = True

                elif item['type'] == 'ETH_DST':
                    if item['mac'] == self.dst_mac:
                        is_dst_same = True
                elif item['type'] == 'IN_PORT':
                    self.in_port = str(item['port'])

        if is_src_same and is_dst_same:
            if self.flow['treatment'] and self.flow['treatment']['deferred']:
                defers = self.flow['treatment']['deferred']
                for item in defers:
                    if item['type'] == 'GROUP':
                        r = re.findall(r'{id=(.+?)}', item['groupId'])
                        if len(r) > 0:
                            self.group_id = r[0]
            return True

        return False

    def parse_output_port(self, groups):
        for group in groups:
            if group['deviceId'] == self.flow['deviceId']:
                group_id_str = hex(int(group['id']))
                if self.group_id is not None:
                    if self.group_id == group_id_str:
                        port_id = get_group_output_port(group)
                        self.out_port = port_id
                        return True

        return False


class LinkManager:
    links = None
    link_dict = {}

    def __init__(self, links):
        self.links = links

    def get_dst(self, src_location):
        for link in self.links:
            if link['src']['device'] + '/' + link['src']['port'] == src_location:
                return link['dst']
        return None
