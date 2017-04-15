# -*- coding: utf-8 -*-
import re
import tools

from lib import art
from lib.cache import Cache
from lib.errors import WebSiteError


class MovistarTV:

    __channels_url = 'http://www.iptvlinksfree.com/category/spain/'

    def __init__(self, settings):
        self.__settings = settings

    def get_menu(self):
        """
        Get MovistarTV channels

        :return: The list of MovistarTV channels
        :rtype: list
        """
        cache = Cache(self.__settings['path'], minutes=360)

        # Busca los canales en cache
        channels = cache.load(self.__channels_url)
        if channels:
            return channels

        # No están en cache, los obtiene
        events = []

        # GET http://www.iptvlinksfree.com/category/spain/
        page = tools.get_web_page(self.__channels_url)
        if not page:
            raise WebSiteError(
                u'La página no está online',
                u'¿Estás conectado a Internet?',
                time=self.__settings['notify_secs']
            )

        # Busca todas URL de canales
        # Una por día, la primera es la lista más reciente
        urls = re.findall(r'href="(.*)" rel="bookmark"', page, re.U)
        if not (urls and type(urls) == list and len(urls) > 0):
            raise WebSiteError(
                u'Lista de canales no encontrada',
                u'Los de Movistar+ han hecho cambios en la Web',
                time=self.__settings['notify_secs']
            )

        # Busca hasta que encuentre una lista de canales o haya buscado en todas
        for url in urls:
            # GET url
            page = tools.get_web_page(url)
            if not page:
                raise WebSiteError(
                    u'La página no está online',
                    u'¿Estás conectado a Internet?',
                    time=self.__settings['notify_secs']
                )

            # Obtiene los nombres y urls de los canales
            chs = re.findall(r'#EXTINF:.*,\W*[E][S][P]?\W*[_]*([0-9A-Za-z]*.*)\s{1,2}(http[s]?://.*)\s', page, re.U)
            if not chs:
                continue

            # Añade los canales encontrados a la lista
            for ch in chs:
                ch_name = tools.str_sanitize(ch[0])
                channel_art = self.__get_art(ch_name)
                events.append({
                    'name': ch_name,
                    'video': tools.str_sanitize(ch[1]),
                    'icon': channel_art['icon'],
                    'fanart': channel_art['fanart']
                })

            break

        if len(events) == 0:
            raise WebSiteError(
                u'Problema en Movistar+',
                u'No se han encontrado canales en la Web',
                time=self.__settings['notify_secs']
            )

        cache.save(self.__channels_url, events)
        return events

    def __get_art(self, channel):
        """
        Get a dict containing the icon and fanart URLs for a given category

        :return: The dict containing icon and fanart for a given category
        :rtype: dict
        """
        return {
            'icon': art.get_channel_icon(channel, self.__settings['path']),
            'fanart': tools.build_path(self.__settings['path'], 'movistar_art.jpg')
        }
