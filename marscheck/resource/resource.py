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
        r = requests.post('http://' + self.mars_config.get_url() + '/mars/useraccount/v1/login', headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, json = auth)
        token=''
        if (r.status_code == 200):
            token = r.headers['MARS_G_SESSION_ID']
        else:
            raise Exception('Http request get token error.')

        requests.packages.urllib3.disable_warnings()
        res = requests.get('https://' + self.mars_config.get_url() + url,
                           headers= {'Cookie': 'marsGSessionId=' + token},
                           verify=False)
        if res.status_code == 200:
            return res.json()
        else:
            raise Exception('Http request with error.')
