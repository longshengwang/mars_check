# -*- coding:utf-8 -*-


class ResourceCompare:
    mars_config = None
    device_config_object = None
    flow_object = None
    group_object = None
    host_object = None

    def __init__(self, mars_config):
        self.mars_config = mars_config

    def compare_hosts(self, before_hosts, after_hosts):
        modify_host_str_list = []
        new_hosts = []

        before_host_dict = {}
        for item in before_hosts:
            before_host_dict[item['mac']] = item

        for item in after_hosts:
            mac = item['mac']
            if mac in before_host_dict:
                before_host = before_host_dict[item['mac']]
                res = self._compare_host(before_host, item)
                modify_host_str_list.append(res)
                del before_host_dict[mac]
            else:
                new_hosts.append(item)
        return {'new': new_hosts, 'removed': before_host_dict.values(), 'modified': modify_host_str_list}

    def compare_flows(self, before_flows, after_flows, device_id_4_compare=None):
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
                    res[device_id] = {'new ': [], 'removed': []}
                res[device_id]['new'].append(item)

        for item in before_flows_dict.values():
            device_id = item['deviceId']

            if device_id_4_compare is not None and device_id_4_compare != device_id:
                continue

            if device_id not in res:
                res[device_id] = {'new ': [], 'removed': []}
            res[device_id]['removed'].append(item)
        return res

    def compare_groups(self, before_groups, after_groups, device_id_4_compare=None):
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
                    res[device_id] = {'new ': [], 'removed': []}
                res[device_id]['new'].append(item)

        for item in before_groups_dict.values():
            device_id = item['deviceId']
            if device_id_4_compare is not None and device_id_4_compare != device_id:
                continue
            if device_id not in res:
                res[device_id] = {'new ': [], 'removed': []}
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

    def compare_link(self, before_links, after_links):
        res = {'new': [], 'removed': []}
        before_links_dict = {}
        for item in before_links:
            link_id = self._get_link_id(item)
            if link_id not in before_links_dict:
                before_links_dict[link_id] = item

        for item in after_links:
            a_link_id = self._get_link_id(item)
            if a_link_id in before_links_dict:
                del before_links_dict[a_link_id]
            else:
                res['new'].append(item)

        for item in before_links_dict.values():
            res['removed'].append(item)

        return res

    def _get_link_id(self, link):
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
    def _compare_host(self, before_host, after_host):
        res = ''

        before_host_ip_str = ','.join(before_host['ipAddresses'].sort())
        after_host_ip_str = ','.join(after_host['ipAddresses'].sort())

        before_host_location_list = []
        for location in before_host['locations']:
            before_host_location_list.append(location['elementId'] + '/' + location['port'])
        before_host_location_list.sort()
        before_host_location_str = ','.join(before_host_location_list)

        after_host_location_list = []
        for location in after_host['locations']:
            after_host_location_list.append(location['elementId'] + '/' + location['port'])
        after_host_location_list.sort()
        after_host_location_str = ','.join(after_host_location_list)

        before_host_last_update = before_host['lastUpdateTime']
        after_host_last_update = after_host['lastUpdateTime']

        if before_host_ip_str != after_host_ip_str:
            res = res + 'ip address: ' + before_host_ip_str + '=>' + after_host_ip_str + ';'
        if before_host_location_str != after_host_location_str:
            res = res + 'location:  ' + before_host_location_str + '=>' + after_host_location_str + ';'
        if before_host_last_update != after_host_last_update:
            res = res + 'lastUpdate:  ' + before_host_last_update + '=>' + after_host_last_update + ';'

        if res == '':
            return None

        return 'Host: ' + before_host['mac'] + '   ' + res
