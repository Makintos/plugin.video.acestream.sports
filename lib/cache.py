# -*- coding: utf-8 -*-
import hashlib
import json
import os

import xbmc

import tools
import datetime
import time


class Cache:

    def __init__(self, path, minutes=30):
        self.__path = path
        self.__minutes = minutes
        cache_dir = xbmc.translatePath(os.path.join(path, 'resources', 'cache'))
        if not os.path.isdir(cache_dir):
            tools.write_log("Creating Cache: '%s'" % cache_dir)
            os.mkdir(cache_dir)

    def load(self, url, log_read_ok=True):
        try:
            with open(tools.build_path(self.__path, '%s.json' % hashlib.sha224(url).hexdigest(), 'cache'), 'r') as fp:
                content = json.load(fp)
            if datetime.datetime.now() <= datetime.datetime.fromtimestamp(content['timestamp']) + \
                    datetime.timedelta(minutes=self.__minutes):
                if log_read_ok:
                    tools.write_log("Cache: '%s' read ok" % url)
                return content['data']
            else:
                tools.write_log("Cache: '%s' expired" % url)
                return None
        except IOError:
            return None

    def save(self, url, data):
        content = {}
        try:
            content['timestamp'] = time.time()
            content['data'] = data
            with open(tools.build_path(self.__path, '%s.json' % hashlib.sha224(url).hexdigest(), 'cache'), 'w') as fp:
                json.dump(content, fp, indent=4)
            tools.write_log("Cache: new '%s'" % url)
        except IOError:
            tools.write_log("Cache: can't write '%s'" % url, xbmc.LOGERROR)
