# -*- coding: utf-8 -*-
import re

import tools

from lib.cache import Cache
from lib.epg import EPG
from lib.errors import WebSiteError


class MovistarTV:

    __channels_url = 'http://iptv.filmover.com/category/spain/'

    def __init__(self, settings):
        self.__settings = settings

    def get_menu(self):
        """
        Get MovistarTV channel lists

        :return: The list of MovistarTV channel lists
        :rtype: list
        """
        cache = Cache(self.__settings['path'], minutes=60)

        # Busca las listas de canales en cache
        ch_lists = cache.load(self.__channels_url)
        if ch_lists:
            return ch_lists

        # No están en cache, los obtiene
        ch_lists = []

        # GET http://iptv.filmover.com/category/spain/
        page = tools.get_web_page(self.__channels_url)

        # Busca todas URL de listas de canales
        # Una por día, la primera es la lista más reciente
        urls = re.findall(r'<h2\s*class="entry-tit.*le">\s*<a href="(.*)"\s*rel="bookmark">(.*)</a></h2>', page, re.U)
        if not (urls and type(urls) == list and len(urls) > 0):
            raise WebSiteError(
                u'Lista de canales no encontrada',
                u'Los de Movistar+ han hecho cambios en la Web',
                time=self.__settings['notify_secs']
            )

        for url in urls:
            ch_lists.append({
                'name': tools.str_sanitize(url[1]),
                'channel_url': tools.str_sanitize(url[0]),
                'icon': tools.build_path(self.__settings['path'], 'movistar.png'),
                'fanart': tools.build_path(self.__settings['path'], 'movistar_art.jpg')
            })

        if len(ch_lists) == 0:
            raise WebSiteError(
                u'Problema en Movistar+',
                u'No se han encontrado listas de canales en la Web',
                time=self.__settings['notify_secs']
            )

        cache.save(self.__channels_url, ch_lists)
        return ch_lists

    def get_channels(self, url):
        cache = Cache(self.__settings['path'], minutes=180)
        epg = EPG(self.__settings)

        # Busca los canales en cache
        channels = cache.load(url)
        if channels:
            # Actualiza la EPG de los canales
            epg.update_metadata(channels)
            return channels

        # No están en cache, los obtiene
        channels = []

        # GET url
        page = tools.get_web_page(url)

        # Obtiene los nombres y urls de los canales
        chs = re.findall(r'#EXTINF:.*,(.*)<br\s/>\s(http[s]?://.*)<', page, re.U)
        if not chs:
            raise WebSiteError(
                u'Problema en Movistar+',
                u'No se han encontrado canales en la lista seleccionada',
                time=self.__settings['notify_secs']
            )

        # Añade los canales encontrados a la lista
        for ch in chs:
            ch_name = tools.str_sanitize(ch[0])
            ch_link = tools.str_sanitize(ch[1])
            if not (ch_link.endswith('.m3u8') or ch_link.endswith('.m3u')):
                channels.append({
                    'name': ch_name,
                    'video': ch_link,
                    'icon': tools.build_path(self.__settings['path'], 'movistar.png'),
                    'fanart': tools.build_path(self.__settings['path'], 'movistar_art.jpg')
                })

        if len(channels) == 0:
            raise WebSiteError(
                u'No hay canales',
                u'La lista no contiene canales que se puedan reproducir',
                time=self.__settings['notify_secs']
            )

        # Añade la EPG a los canales
        epg.add_metadata(channels)

        # Guarda los canales en caché y los devuelve
        cache.save(url, channels)
        return channels
