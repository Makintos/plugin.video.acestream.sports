# -*- coding: utf-8 -*-
import os
import random
import urllib2

import xbmc
import xbmcgui
import xbmcaddon
import platform

import json
import re


# Constants
from lib.cache import Cache
from lib.errors import WebSiteError


def STRING():
    return 0


def BOOL():
    return 1


def NUM():
    return 2


def write_log(message, level=xbmc.LOGNOTICE):
    xbmc.log('[Acestream.Sports] %s' % message.encode('utf-8'), level)


def str_sanitize(text):
    return str(text.encode('utf8').replace('\t', '').replace('\n', ' ')).strip()


def random_agent():
    browser_version = [
        [
            '%s.0' % i for i in xrange(39, 46)
        ],
        [
            '37.0.2062.103', '37.0.2062.120', '37.0.2062.124',
            '38.0.2125.101', '38.0.2125.104', '38.0.2125.111',
            '39.0.2171.71', '39.0.2171.95', '39.0.2171.99',
            '40.0.2214.93', '40.0.2214.111', '40.0.2214.115',
            '42.0.2311.90', '42.0.2311.135', '42.0.2311.152',
            '43.0.2357.81', '43.0.2357.124',
            '44.0.2403.155', '44.0.2403.157',
            '45.0.2454.101', '45.0.2454.85',
            '46.0.2490.71', '46.0.2490.80', '46.0.2490.86',
            '47.0.2526.73', '47.0.2526.80'
        ],
        ['11.0']
    ]

    win_version = [
        'Windows NT 10.0',
        'Windows NT 7.0',
        'Windows NT 6.3',
        'Windows NT 6.2',
        'Windows NT 6.1',
        'Windows NT 6.0',
        'Windows NT 5.1',
        'Windows NT 5.0'
    ]

    features = [
        '; WOW64',
        '; Win64; IA64',
        '; Win64; x64',
        ''
    ]

    user_agents = [
        'Mozilla/5.0 ({win_ver}{feature}; rv:{br_ver}) Gecko/20100101 Firefox/{br_ver}',
        'Mozilla/5.0 ({win_ver}{feature}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{br_ver} Safari/537.36',
        'Mozilla/5.0 ({win_ver}{feature}; Trident/7.0; rv:{br_ver}) like Gecko'
    ]

    index = random.randrange(len(user_agents))

    return user_agents[index].format(
        win_ver=random.choice(win_version),
        feature=random.choice(features),
        br_ver=random.choice(browser_version[index])
    )


def get_web_page(url):
    try:
        req = urllib2.Request(url)
        req.add_header('User-Agent', random_agent())
        response = urllib2.urlopen(req)
        content = response.read().decode(response.headers.getparam('charset') or 'utf-8')
        response.close()
        write_log('GET %i %s' % (response.getcode(), url))
        if response.getcode() == 200:
            return content
        return None
    except:
        write_log('Exception on GET %s' % url, xbmc.LOGERROR)
        raise WebSiteError(
            u'Error de conexión',
            u'Se ha producido un error en Kodi',
            time=6000
        )


def get_hashlink(url, settings, minutes=10):
    cache = Cache(settings['path'], minutes=minutes)

    # Busca el hash en cache
    c_hash = cache.load(url)
    if c_hash:
        return c_hash['hash']

    # No está en cache, lo obtiene
    page = get_web_page(url)
    if not page:
        raise WebSiteError(
            u'Error de conexión',
            u'¿Estás conectado a Internet?',
            time=settings['notify_secs']
        )

    ace_hash = re.search(r'.*loadPlayer\(\"([a-f0-9]{40})\",.*', page, re.U).groups()
    if not ace_hash:
        write_log("Hashlink no encontrado en '%s'" % url, xbmc.LOGERROR)
        raise WebSiteError(
            u'Enlace no encontrado',
            u'Puede que hayan hecho cambios en la Web',
            time=settings['notify_secs']
        )

    # Guarda el hash en caché
    cache.save(url, {"hash": ace_hash[0]})

    return ace_hash[0]


def build_path(path, file_name, resource='images'):
    return xbmc.translatePath(os.path.join(path, 'resources', resource, file_name))


class Notify(object):
    def __init__(self):
        self.prev_header = ''
        self.prev_message = ''

    def notify(self, header, message, icon=xbmcgui.NOTIFICATION_INFO, disp_time=5000, repeat=False):
        if repeat or (header != self.prev_header or message != self.prev_message):
            xbmcgui.Dialog().notification(header.encode('utf-8'), message.encode('utf-8'), icon, disp_time)
        else:
            write_log('Message content is same as before, don\'t show notification')
        self.prev_header = header
        self.prev_message = message


class Release(object):
    def __init__(self):
        item = {}
        self.platform = platform.system()
        self.hostname = platform.node()
        if self.platform == 'Linux':
            with open('/etc/os-release', 'r') as _file:
                item = {}
                for _line in _file:
                    parameter, value = _line.split('=')
                    item[parameter] = value

        self.os_name = item.get('NAME')
        self.os_id = item.get('ID')
        self.os_version = item.get('VERSION_ID')


def show_dialog_ok(header, message):
    xbmcgui.Dialog().ok(header.encode('utf-8'), message.encode('utf-8'))


def jsonrpc(query):
    querystring = {"jsonrpc": "2.0", "id": 1}
    querystring.update(query)
    return json.loads(xbmc.executeJSONRPC(json.dumps(querystring, encoding='utf-8')))


def get_addon_setting(setting, s_type=STRING, multiplicator=1):
    if s_type == BOOL:
        _ret = True if xbmcaddon.Addon().getSetting(setting).upper() == 'TRUE' else False
    elif s_type == NUM:
        try:
            _ret = int(re.match('\d+', xbmcaddon.Addon().getSetting(setting)).group()) * multiplicator
        except AttributeError:
            _ret = 0
    else:
        _ret = xbmcaddon.Addon().getSetting(setting)
    # writeLog('Load setting %s [%s]: %s' %
    # (setting, re.compile("<type '(.+?)'>", re.DOTALL).findall(str(type(_ret)))[0], _ret))
    return _ret
