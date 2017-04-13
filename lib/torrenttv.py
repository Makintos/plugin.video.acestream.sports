# -*- coding: utf-8 -*-
import re
import tools
from lib import lang, art

from lib.cache import Cache
from lib.errors import WebSiteError


class TorrentTV:

    __agenda_url = 'http://super-pomoyka.us.to/trash/ttv-list/ttv.json'

    def __init__(self, settings):
        self.__settings = settings

    def get_menu(self):
        """
        Get the Torrent-TV.ru genres menu

        :return: The list of Torrent-TV.ru genres
        :rtype: list
        """
        genre_events = []
        genres = []
        genres_list = []
        events = self.__get_all_events()

        # Lista de categorias en la guía
        for event in events:
            if event['cat'] not in genres:
                genres.append(event['cat'])

        # Construye la lista géneros: añade al título el número de eventos que contiene
        for genre in genres:
            genre_events[:] = []
            genre_art = art.get_genre_art(genre, self.__settings['path'])
            for event in events:
                if event['cat'] == genre:
                    genre_events.append(genre)
            genre_id = lang.es.get(genre[1:], None)
            if genre_id and (genre_id != 'Adultos' or self.__settings['adult']):
                genres_list.append({
                    'name': '[B]%s[/B] (%i)' % (genre_id, len(genre_events)),
                    'genre_id': genre_id,
                    'icon': genre_art['icon'],
                    'fanart': genre_art['fanart']
                })

        return genres_list

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
            raise WebSiteError(
                u'La página no está online',
                u'¿Estás conectado a Internet?',
                time=self.__settings['notify_secs']
            )

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

    def get_events_by_genre(self, genre):
        """
        Get Torrent-TV.ru events by a given genre

        :param genre: The genre name
        :type: genre: str
        :return: The list of Torrent-TV.ru events
        :rtype: list
        """
        genres = []
        events = self.__get_all_events()

        for event in events:
            if lang.es.get(event['cat'][1:]) == genre:
                genre_art = art.get_genre_art(event['cat'], self.__settings['path'])
                genres.append({
                    'name': event['name'],
                    'icon': genre_art['icon'],
                    'fanart': genre_art['fanart'],
                    'hash': event['url']
                })

        return genres
