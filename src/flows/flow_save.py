# -*- coding:utf8 -*-
import requests
from requests.auth import HTTPBasicAuth


class FlowSave:
    def __init__(self):
        pass

    def dump_flows(self):
        pass


userData = {}

h = requests.get("https://210.63.204.28/mars/v1/flows", auth=HTTPBasicAuth('karaf', 'karaf'), verify=False)
print h.content
j = h.json()

# print j['devices']
