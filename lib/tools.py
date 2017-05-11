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

from lib.cache import Cache
from lib.cloudflare import Cloudflare
from lib.errors import WebSiteError


# Constants
def STRING():
    return 0


def BOOL():
    return 1


def NUM():
    return 2


def write_log(message, level=xbmc.LOGNOTICE):
    xbmc.log('[Acestream.Sports] %s' % message.encode('utf-8'), level)


def str_sanitize(text):
    return re.sub(r'<[^>]*>', '', str_unescape(
        text.encode('utf8').replace('\t', '').replace('\n', ' ').replace('  ', ' ')
    ).strip())


def str_unescape(strn):
    return strn.replace('&quot;', '"')\
        .replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&').replace('\/', '/').replace('&#039;', "'")


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


def get_web_page(url, cfduid=None, cookie=None, agent=None):
    try:
        req = urllib2.Request(url)
        user_agent = agent if agent else random_agent()
        req.add_header('User-Agent', user_agent)
        if cookie or cfduid:
            req.add_header('Host', url.split('/')[2])
            req.add_header('Connection', 'keep-alive')
            req.add_header('Cache-Control', 'max-age=0')
            req.add_header('Upgrade-Insecure-Requests', 1)
            req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
            req.add_header('DNT', 1)
            req.add_header('Referer', url)
            req.add_header('Accept-Language', 'es-ES,es;q=0.8')
            req.add_header('Cookie', cookie if cookie else cfduid)
        response = urllib2.urlopen(req)
        headers = response.headers.dict
        content = response.read().decode(response.headers.getparam('charset') or 'utf-8')
        response.close()
        if response.getcode() == 200:
            if not cookie and 'server' in headers and 'cloudflare' in headers['server']:
                write_log('GET %i CloudFlare %s' % (response.getcode(), url))
                cfduid = re.findall(r'__cfduid=[\w\d]+', headers['set-cookie'], re.U)
                cookie = re.findall(r'document.cookie=[\'"]?([^;,\'" ]+)', content, re.U)
                if not cfduid or not cookie:
                    return content
                return get_web_page(url, cfduid[0], '%s; %s' % (cfduid[0], cookie[0]), user_agent)
            else:
                write_log('GET %i %s' % (response.getcode(), url))
                return content
        else:
            raise urllib2.HTTPError
    except urllib2.HTTPError, e:
        if e.code == 404:
            write_log('HTTPError 404 on GET %s' % url, xbmc.LOGERROR)
            raise WebSiteError(
                u'La página no existe',
                u'Seguramente estén actualizando la agenda. Inténtalo más tarde...',
                time=5000
            )
        cf = Cloudflare({
            'url': url,
            'data': e.read().decode(e.headers.getparam('charset') or 'utf-8'),
            'headers': e.headers.dict
        })
        if cf.is_cloudflare:
            return get_web_page(cf.get_auth_url(), cf.get_cfduid())
        else:
            write_log('HTTPError %i on GET %s' % (e.code, url), xbmc.LOGERROR)
            raise WebSiteError(
                u'Error de conexión',
                u'La web se ha caído, inténtalo en otra',
                time=5000
            )
    except urllib2.URLError, e:
        write_log('URL error on GET %s: %s' % (url, e), xbmc.LOGERROR)
        raise WebSiteError(
            u'Error de conexión',
            u'No hay conexión a Internet o la Web ya no existe...',
            time=5000
        )
    except ValueError, e:
        write_log('Value error on GET %s: %s' % (url, e), xbmc.LOGERROR)
        raise WebSiteError(
            u'URL mal formada',
            u'Han hecho cambios en la Web, inténtalo en otra...',
            time=5000
        )


def get_hashlink(url, settings, minutes=10):
    # ¿La URL contiene el hashlink?
    if 'http' not in url:
        ace_hash = re.findall(r'([a-f0-9]{40})', url, re.U)
        if ace_hash:
            return url[12:]
        else:
            write_log("URL mal formada: '%s'" % url, xbmc.LOGERROR)
            raise WebSiteError(
                u'Enlace mal formado',
                u'Puede que hayan hecho cambios en la Web',
                time=settings['notify_secs']
            )

    # Busca el hash en cache
    cache = Cache(settings['path'], minutes=minutes)
    c_hash = cache.load(url)
    if c_hash:
        return c_hash['hash']

    # No está en cache, lo obtiene
    page = get_web_page(url)

    # Busca el hash de acestream
    ace_hash = find_hash(page)
    if not ace_hash:
        # No lo ha encontrado, busca una URL que pueda contener el hash
        hash_url = find_hash_url(page)
        if hash_url:
            # Hay URL, busca el hash en la nueva página
            page = get_web_page(hash_url)
            ace_hash = find_hash(page)

    if not ace_hash:
        write_log("Hashlink no encontrado en '%s'" % url, xbmc.LOGERROR)
        raise WebSiteError(
            u'Enlace no encontrado',
            u'El enlace está en otra página y no se puede llegar a él',
            time=settings['notify_secs']
        )

    # Guarda el hash en caché
    cache.save(url, {"hash": ace_hash})

    return ace_hash


def find_hash(page):
    ace_hash = re.search(r'.*loadPlayer\(\"([a-f0-9]{40})\",.*', page, re.U)
    return ace_hash.groups()[0] if ace_hash else None


def find_hash_url(page):
    # RegEx para Rivo ACEXX
    hash_url = re.findall(r'<iframe\s*id="player"\s*src=[\'"](.*)[\'"]\s+width=', page, re.U)
    if hash_url:
        return hash_url[0]
    return None


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
