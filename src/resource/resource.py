# -*- coding:utf-8 -*-

import json

import requests
from requests.auth import HTTPBasicAuth


class Resource:
    name = 'base'
    mars_config = None

    def __init__(self, mars_config):
        self.mars_config = mars_config

    def get_data(self):
        return ''

    def save(self, path):
        name = self.get_name()
        f = open(path + '/' + name, 'w')
        f.write(json.dumps(self.get_data()))
        f.close()

    def get_name(self):
        return self.name

    def get(self, url):
        auth = self.mars_config.get_auth()
        requests.packages.urllib3.disable_warnings()

        res = requests.get(self.mars_config.get_url() + url,
                           auth=HTTPBasicAuth(auth['user_name'], auth['password']),
                           verify=False)
        if res.status_code == 200:
            return res.json()
        else:
            raise Exception('Http request with error.')
