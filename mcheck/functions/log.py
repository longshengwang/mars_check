# -*- coding:utf8 -*-

# 'https://192.168.200.148/mars/utility/logs/v1/controller?
# match=device&number=1000&source=%2Froot%2Fonos%2Fapache-karaf-3.0.8%2Fdata%2Flog%2Fkaraf.log&start=2020-11-23T06:56:00.000Z' \

from lib.color import STYLE, UseStyle
from resource.resource import Resource
from utils import utc_time_str_2_time_stamp, format_time_stamp_2_string, time_stamp_2_utc_time_str
import time

RED_NUMBER = STYLE['fore']['red']
YELLOW_NUMBER = STYLE['fore']['yellow']
BLUE_NUMBER = STYLE['fore']['blue']
PURPLE_NUMBER = STYLE['fore']['purple']
CYAN_NUMBER = STYLE['fore']['cyan']
GREEN_NUMBER = STYLE['fore']['green']


class Log:
    mars_config = None

    url = '/mars/utility/logs/v1/controller'

    def __init__(self, mars_config):
        self.mars_config = mars_config

    def show(self, word, count=1000, last_hours=2):
        resource = Resource(self.mars_config)
        utc_time_str = time_stamp_2_utc_time_str(time.time() - last_hours * 60 * 60)

        query_url = self.url + '?number=' + str(count) + \
                    '&source=%2Froot%2Fonos%2Fapache-karaf-3.0.8%2Fdata%2Flog%2Fkaraf.log' \
                    '&start=' + utc_time_str \
                    + '&match=' + word

        res = resource.get(query_url)
        # res_json = json.loads(res)
        for item in res['logs']:
            print self._re_color(item)

    def _re_color(self, word):
        item = word.replace('<em>', '\033[' + str(GREEN_NUMBER) + 'm')
        item = item.replace('</em>', '\033[0m')

        item = item.replace('INFO', '\033[' + str(GREEN_NUMBER) + 'mINFO\033[0m')
        item = item.replace('WARN', '\033[' + str(YELLOW_NUMBER) + 'mWARN\033[0m')
        item = item.replace('ERROR', '\033[' + str(RED_NUMBER) + 'mERROR\033[0m')

        utc_time_word = item.split('|')[0].strip()

        try:
            local_time = utc_time_str_2_time_stamp(utc_time_word)
            time_word = format_time_stamp_2_string(local_time, is_mill=False)
            time_word_with_mill = time_word + '.' + utc_time_word[-4:-1]
            item = UseStyle(time_word_with_mill, fore='blue') + item[len(utc_time_word):]
            return item
        except Exception, e:
            return word
