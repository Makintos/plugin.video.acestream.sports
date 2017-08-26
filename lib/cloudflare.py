# -*- coding: utf-8 -*-

import re
import urllib
import urlparse

import xbmc

import tools


class Cloudflare:

    def __init__(self, response):
        self.__is_cloudflare = True

        if not ('challenge-form' and 's,t,o,p,b,r,e,a,k,i,n,g,f' and 'jschl-answer' in response['data']):
            tools.write_log('[ERROR] CloudFlare ha cambiado de reto')
            self.__is_cloudflare = False
            return

        # noinspection PyBroadException
        try:
            self.__cfduid = re.findall(r'__cfduid=[\w\d]+', response['headers']['set-cookie'], re.U)
            self.__wait = int(re.findall(r'\}, ([\d]+)\);', response["data"], re.U)[0])
            challenge = re.findall(r'challenge-form\'\);\s*(.*)a.v', response['data'], re.U)[0]
            javascript = re.findall(r'setTimeout\(function\(\){\s*.*?.*:(.*?)};', response['data'], re.U)[0]
            jschl_vc = re.findall(r'name="jschl_vc" value="(.+?)"/>', response['data'], re.U)[0]
            js_value = self.__decode(javascript)

            for line in challenge.split(';'):
                sections = line.split('=')
                value = self.__decode(sections[1])
                js_value = int(eval("{0}{1}{2}".format(str(js_value), sections[0][-1], str(value))))

            answer = js_value + len(urlparse.urlparse(response['url']).netloc)

            url = '/'.join(response['url'].split('/')[:-1])
            if '<form id="challenge-form" action="/cdn' in response['data']:
                url = '/'.join(response['url'].split('/')[:3])

            if 'type="hidden" name="pass"' in response['data']:
                self.__auth_url = '%s/cdn-cgi/l/chk_jschl?pass=%s&jschl_vc=%s&jschl_answer=%s' % (
                    url,
                    urllib.quote_plus(re.compile('name="pass" value="(.*?)"').findall(response['data'])[0]),
                    jschl_vc,
                    answer
                )
                tools.write_log("WAIT %s..." % self.__wait)
                xbmc.sleep(self.__wait)
            else:
                self.__auth_url = urlparse.urljoin(
                    response['url'], '/cdn-cgi/l/chk_jschl?jschl_vc=%s&jschl_answer=%s' % (jschl_vc, answer)
                )
        except:
            tools.write_log('[ERROR] CloudFlare ha reventado en pleno reto javascript')
            self.__is_cloudflare = False
            return

        if not self.__auth_url and "refresh" in response["headers"]:
            self.__header_data = {}
            # noinspection PyBroadException
            try:
                self.__wait = int(response["headers"]["refresh"].split(";")[0])
                self.__auth_url = "%s%s?%s" % (
                    '/'.join(response['url'].split('/')[:-1]),
                    response["headers"]["refresh"].split("=")[1].split("?")[0],
                    urllib.urlencode({'pass': response["headers"]["refresh"].split("=")[2]})
                )
                tools.write_log("WAIT %ss..." % self.__wait)
                xbmc.sleep(self.__wait)
            except:
                tools.write_log('[ERROR] CloudFlare ha reventado en pleno reto (headers)')
                self.__is_cloudflare = False
                return

    @staticmethod
    def __decode(s):
        # noinspection PyBroadException
        try:
            offset = 1 if s[0] == '+' else 0
            val = int(
                eval(s.replace('!+[]', '1').replace('!![]', '1').replace('[]', '0').replace('(', 'str(')[offset:]))
            return val
        except:
            pass

    def get_cfduid(self):
        return self.__cfduid

    def is_cloudflare(self):
        return self.__is_cloudflare
    
    def get_auth_url(self):
        return self.__auth_url
