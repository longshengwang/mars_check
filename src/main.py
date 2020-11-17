# -*- coding:utf8 -*-

import os
from os.path import expanduser
from config import MarsConfig
from functions.snap_data import SnapData

DEFAULT_CONFIG_PATH = '/.mars_check/'
MAX_BACKUP_COUNT = 20


def run():
    init_config_dir()


def init_config_dir():
    home = expanduser("~")
    if not os.path.exists(home + DEFAULT_CONFIG_PATH):
        os.mkdir(home + DEFAULT_CONFIG_PATH)


if __name__ == '__main__':
    # import sys
    # sys.path.append("..")
    # a = {}
    # from lib.color import UseStyle
    # import json
    #
    #
    #
    #
    # a['a'] = "\u001b[31mdddd\u001b[0m"
    #
    # # a[UseStyle('ad','red')] = 'dddd'
    # d = json.dumps(a)
    # print type(d)
    # r = UseStyle('a', fore='red')
    # d = d.replace("a", r)
    # print d
    # print UseStyle('aaa', fore='red') + "dddd"
    run()

    mars_config = MarsConfig("https://210.63.204.28", 'karaf', 'karaf', expanduser("~") + DEFAULT_CONFIG_PATH)
    # snap = SnapData(mars_config)
    # snap.snap_all_data()
    from functions.pre_check import PreCheck
    prechekc = PreCheck(mars_config)
    prechekc.check()




