# -*- coding: utf-8 -*-
import re

import tools
from lib import art, lang
from lib.cache import Cache
from lib.errors import WebSiteError


class TorrentTV:

    __agenda_url = 'http://91.92.66.82/trash/ttv-list/ttv.json'

    def __init__(self, settings):
        self.__settings = settings

    def get_menu(self):
        """
        Get the Torrent-TV.ru categories menu

        :return: The list of Torrent-TV.ru categories
        :rtype: list
        """
        category_events = []
        categories = []
        categories_list = []
        events = self.__get_all_events()

        # Lista de categorias en la guía
        for event in events:
            if event['cat'] not in categories:
                categories.append(event['cat'])

        # Construye la lista categorias: añade al título el número de eventos que contiene
        for category in categories:
            category_events[:] = []
            category_art = self.__get_art(category)
            for event in events:
                if event['cat'] == category:
                    category_events.append(category)
            category_id = lang.genre(category[1:])
            if category_id and (category_id != 'Adultos' or self.__settings['adult']):
                categories_list.append({
                    'name': '[B]%s[/B] (%i)' % (category_id, len(category_events)),
                    'category_id': category_id,
                    'icon': category_art['icon'],
                    'fanart': category_art['fanart']
                })

        return categories_list

    def __get_art(self, category):
        """
        Get a dict containing the icon and fanart URLs for a given category

        :return: The dict containing icon and fanart for a given category
        :rtype: dict
        """
        return art.get_genre_art(lang.genre(category[1:]), self.__settings['path'])

    def __get_all_events(self):
        """
        Get all Torrent-TV.ru events

        :return: The list of Torrent-TV.ru events
        :rtype: list
        """
        cache = Cache(self.__settings['path'])

        # Busca la agenda en cache
        events = cache.load(self.__agenda_url)
        if events:
            return events

        # No está en cache, la obtiene
        events = []

        # GET http://super-pomoyka.us.to/trash/ttv-list/ttv.json
        channels = tools.get_web_page(self.__agenda_url)

        # Busca todas las etiquetas name, url y cat
        # y las guarda en una lista de tuplas ('etiqueta', 'valor')
        data = re.findall(r'(name|url|cat)":"([^"]*)"', channels, re.U)
        if not (data and type(data) == list and len(data) > 0):
            raise WebSiteError(
                u'Lista de canales no encontrada',
                u'Los de TorrentTV.ru han hecho cambios en la Web',
                time=self.__settings['notify_secs']
            )

        # Recorre la lista de 3 en 3
        for x in range(0, len(data) / 3):
            name = data[x * 3][1]
            url = data[x * 3 + 1][1]
            cat = data[x * 3 + 2][1]
            events.append({
                'name': name,
                'url': url,
                'cat': cat
            })

        if len(events) == 0:
            raise WebSiteError(
                u'Problema en TorrentTV',
                u'No hay canales o no hay enlaces en la Web',
                time=self.__settings['notify_secs']
            )

        cache.save(self.__agenda_url, events)
        return events

    def get_channels_by_category(self, category):
        """
        Get Torrent-TV.ru events by a given category

        :param category: The category name
        :type: category: str
        :return: The list of Torrent-TV.ru events
        :rtype: list
        """
        categories = []
        events = self.__get_all_events()

        for event in events:
            if lang.genre(event['cat'][1:]) == category:
                event_art = self.__get_art(event['cat'])
                categories.append({
                    'name': event['name'],
                    'icon': event_art['icon'],
                    'fanart': event_art['fanart'],
                    'hash': event['url']
                })

        return categories
