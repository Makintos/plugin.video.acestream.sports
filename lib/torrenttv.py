# -*- coding: utf-8 -*-
import re

import tools
from lib.cache import Cache


class TorrentTV:

    __agenda_url = 'http://super-pomoyka.us.to/trash/ttv-list/ttv.json'

    # TODO: sacar esto de aquí
    __translations = {
        u'узыка': 'Música',
        u'ознавательные': 'Educativo',
        u'ротика': 'Adultos',
        u'ильмы': 'Películas',
        u'порт': 'Deportes'
    }

    def __build_thumbs(self):
        self.__art = {
            'Música': {
                'icon': tools.build_path(self.__settings['path'], 'musica.png'),
                'fanart': tools.build_path(self.__settings['path'], 'musica_art.jpg')
            },
            'Educativo': {
                'icon': tools.build_path(self.__settings['path'], 'educativo.png'),
                'fanart': tools.build_path(self.__settings['path'], 'educativo_art.jpg')
            },
            'Adultos': {
                'icon': tools.build_path(self.__settings['path'], 'adultos.png'),
                'fanart': tools.build_path(self.__settings['path'], 'adultos_art.jpg')
            },
            'Películas': {
                'icon': tools.build_path(self.__settings['path'], 'peliculas.png'),
                'fanart': tools.build_path(self.__settings['path'], 'ttv_art.jpg')
            },
            'Deportes': {
                'icon': tools.build_path(self.__settings['path'], 'sports.png'),
                'fanart': tools.build_path(self.__settings['path'], 'sports_art.jpg')
            }
        }

    def __init__(self, settings):
        self.__settings = settings
        self.__build_thumbs()

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
            category_id = self.__translations.get(category[1:], None)
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
        return self.__art.get(self.__translations.get(category[1:]), {
            'icon': tools.build_path(self.__settings['path'], 'sports.png'),
            'fanart': tools.build_path(self.__settings['path'], 'sports_art.jpg')
        })

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
        if not channels:
            return events

        # Busca todas las etiquetas name, url y cat
        # y las guarda en una lista de tuplas ('etiqueta', 'valor')
        data = re.findall(r'(name|url|cat)":"([^"]*)"', channels, re.U)
        if not (data and type(data) == list and len(data) > 0):
            return events

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
            return events

        cache.save(self.__agenda_url, events)
        return events

    def get_events_by_category(self, category):
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
            if self.__translations.get(event['cat'][1:]) == category:
                art = self.__get_art(event['cat'])
                categories.append({
                    'name': event['name'],
                    'icon': art['icon'],
                    'fanart': art['fanart'],
                    'hash': event['url']
                })

        return categories
