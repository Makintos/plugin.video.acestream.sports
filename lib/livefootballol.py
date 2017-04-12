# -*- coding: utf-8 -*-
import datetime
import re
import tools

import xbmc

from bs4 import BeautifulSoup
from lib.cache import Cache
from lib.errors import WebSiteError


class LiveFootbalLOL:

    __web_url = 'http://livefootballol.me/'

    # TODO: sacar esto de aquí
    __translations = {
        'Spanish Primera Division': 'La Liga',
        'Spanish Segunda Division': 'La Liga 123',
        'English Premier League': 'Liga Inglesa',
        'French Ligue 1': 'Liga Francesa',
        'Italian Serie A': 'Liga Italiana',
        'German Bundesliga': 'Liga Alemana'
    }

    def __build_thumbs(self):
        self.__competition_thumbs = {
            'UEFA Champions League': tools.build_path(self.__settings['path'], 'champions_league.png'),
            'UEFA Europa League': tools.build_path(self.__settings['path'], 'europa_league.jpg'),
            'Spanish Primera Division': tools.build_path(self.__settings['path'], 'liga_es_1.png'),
            'English Premier League': tools.build_path(self.__settings['path'], 'liga_en.png'),
            'French Ligue 1': tools.build_path(self.__settings['path'], 'liga_fr.png'),
            'Italian Serie A': tools.build_path(self.__settings['path'], 'liga_it_serie_a.png'),
            'German Bundesliga': tools.build_path(self.__settings['path'], 'liga_de_1.png'),
        }

    def __init__(self, settings):
        self.__settings = settings
        self.__build_thumbs()

    def get_menu(self):
        """
        Get the list of LiveFootbalLOL categories: agenda and competitions

        :return: The list of LiveFootbalLOL categories
        :rtype: list
        """
        return [
            {
                'name': 'Hoy y mañana',
                'icon': tools.build_path(self.__settings['path'], 'hoy_manana.png'),
            }, {
                'name': 'Agenda 7 días',
                'icon': tools.build_path(self.__settings['path'], 'siete_dias.png'),
            }, {
                'name': 'Competiciones',
                'icon': tools.build_path(self.__settings['path'], 'competiciones.png'),
            }]

    def __get_competition_art(self, competition):
        return {
            'icon': self.__competition_thumbs.get(
                tools.str_sanitize(competition),
                tools.build_path(self.__settings['path'], 'futbol.png')),
            'fanart': tools.build_path(self.__settings['path'], 'futbol_art.jpg')
        }

    def __get_urls(self, page):
        agenda_url = None
        url = re.findall(r'href=[\'"]?([^\'" >]+).*title="Live Football Streaming"', page, re.U)
        if url and len(url) == 1:
            agenda_url = url[0] if 'http' in url[0] else '%s%s' % (self.__web_url, url[0])
        if agenda_url:
            return {'agenda': agenda_url}
        return None

    def get_all_events(self):
        """
        Get all LiveFootbalLOL events

        :return: The list of LiveFootbalLOL events
        :rtype: list
        """
        cache = Cache(self.__settings['path'])

        # Busca la URI de la agenda y los enlaces de los canales en caché
        page = cache.load(self.__web_url, False)
        if page:
            # La URI de la agenda está en caché, busca también los eventos
            events = cache.load(page['agenda'])
            if events:
                for event in events:
                    event['name'] = tools.get_event_name(
                        event['event'],
                        event['date'],
                        event['time'],
                        self.__translations.get(event['competition'], event['competition'])
                    )
                return events

        # La URI de la agenda no está en cache
        # Vuelve a obtener la agenda y los eventos
        events = []

        # GET livefootballol.in
        page = tools.get_web_page(self.__web_url)
        if not page:
            raise WebSiteError(u'La página no está online', u'¿Estás conectado a Internet?', time=8000)

        # Averigua la URI de la agenda
        urls = self.__get_urls(page)
        if not urls:
            raise WebSiteError(u'Agenda no encontrada', u'Los de LiveFootbalLOL han hecho cambios en la Web', time=6000)

        # Guarda la URI de la agenda en caché
        cache.save(self.__web_url, urls)

        # GET agenda
        agenda = tools.get_web_page(urls['agenda'])
        if not agenda:
            raise WebSiteError(u'Error de conexión', u'¿Estás conectado a Internet?', time=8000)

        # Obtiene la tabla de eventos
        a_events = re.findall(
            r'([0-9]{1,2}:[0-9]{2}).*\[(.*)\].*<a href=[\'"]?(.*[0-9]{2}-[0-9]{2}-[0-9]{4}-.*)[\'"]>(.*)</a>',
            agenda,
            re.U)

        for a_event in a_events:
            art = self.__get_competition_art(a_event[1])
            c_date = re.findall(r'([0-9]{2}-[0-9]{2}-[0-9]{4})-', tools.str_sanitize(a_event[2]), re.U)
            if c_date:
                events.append(
                    {
                        'date': c_date[0],
                        'time': tools.str_sanitize(a_event[0]),
                        'competition': tools.str_sanitize(a_event[1]),
                        'event': tools.str_sanitize(a_event[3]),
                        'channel_url': a_event[2],
                        'name': tools.get_event_name(
                            tools.str_sanitize(a_event[3]),
                            c_date[0],
                            tools.str_sanitize(a_event[0]),
                            self.__translations.get(tools.str_sanitize(a_event[1]),
                                                    tools.str_sanitize(a_event[1]))),
                        'icon': art['icon'],
                        'fanart': art['fanart']
                    }
                )

        if len(events) == 0:
            raise WebSiteError(
                u'Problema en la agenda',
                u'Está vacía o no hay enlaces, ve a la Web y compruébalo',
                time=8000
            )

        # Guarda los eventos en caché
        cache.save(urls['agenda'], events)

        return events

    def get_events_today_and_tomorrow(self):
        """
        Get today and tomorrow LiveFootbalLOL events

        :return: The list of LiveFootbalLOL events
        :rtype: list
        """
        today_tomorrow = []
        today = datetime.datetime.now()
        events = self.get_all_events()

        for event in events:
            try:
                if int(event['date'][:2]) == int(today.strftime('%d')) or \
                        int(event['date'][:2]) == int((today + datetime.timedelta(days=1)).strftime('%d')):
                    today_tomorrow.append(event)
            except ValueError:
                tools.write_log("Fecha '%s' de '%s' incorrecta" % (event['date'], event['name']), xbmc.LOGERROR)

        return today_tomorrow

    def get_events_by_competition(self, competition):
        """
        Get LiveFootbalLOL events by a given competition

        :param competition: The competition name
        :type: competition: str
        :return: The list of LiveFootbalLOL events
        :rtype: list
        """
        competitions = []
        events = self.get_all_events()

        for event in events:
            if event['competition'] == competition:
                competitions.append(event)

        return competitions

    def get_competitions(self):
        competition_events = []
        competitions = []
        competitions_list = []
        events = self.get_all_events()

        # Lista de competiciones en la guía
        for event in events:
            if not event['competition'] in competitions:
                competitions.append(event['competition'])

        # Construye la lista competiciones: añade al título el número de eventos que contiene
        for competition in competitions:
            competition_events[:] = []
            competition_art = self.__get_competition_art(competition)
            for event in events:
                if event['competition'] == competition:
                    competition_events.append(competition)
            competitions_list.append({
                'name': '[B]%s[/B] (%i)' % (self.__translations.get(competition, competition), len(competition_events)),
                'competition_id': competition,
                'icon': competition_art['icon'],
                'fanart': competition_art['fanart']
            })

        return competitions_list

    def get_event_links(self, event_url):
        """
        Get LiveFootbalLOL event links by a given event URL

        :param event_url: The event URL
        :type: event_url: str
        :return: The list of LiveFootbalLOL event links
        :rtype: list
        """
        cache = Cache(self.__settings['path'], minutes=5)

        # Busca los canales del evento en caché
        channels = cache.load(event_url, False)
        if channels:
            return channels

        # Los datos de los canales no están en cache
        # Vuelve a obtenerlos
        channels = []

        # GET event_url
        page = tools.get_web_page('%s%s' % (self.__web_url, event_url))
        if not page:
            tools.write_log('No se pueden extraer los enlaces: ' + event_url, xbmc.LOGERROR)
            raise WebSiteError(
                u'Error de conexión',
                u'¿Estás conectado a Internet?',
                time=8000
            )

        # Busca la jornada
        # match_week = re.findall(r'[Mm][Aa][Tt][Cc][Hh]\s[Ww][Ee]{2}[Kk]</td>\s*<td>([0-9]+)</td>', page, re.U)

        # Obtiene la tabla de datos de los canales
        soup = BeautifulSoup(page, 'html5lib')
        table = soup.find('table', attrs={'class': 'uk-table uk-table-hover uk-table-striped'})

        # Obtiene los datos de los canales
        prev_lang = None
        for row in table.findAll("tr")[2:]:
            cells = row.findAll("td")

            # Obtiene los datos generales del canal
            ch_name = tools.str_sanitize(cells[1].get_text())
            ch_lang = tools.str_sanitize(cells[0].get_text())

            # ¿Hay ya enlaces?
            if 'will be here' in ch_name:
                match = re.findall(r'[Mm][Aa][Tt][Cc][Hh]</td>\s*<td><strong>(.*)</strong></td>', page, re.U)
                raise WebSiteError(
                    match[0] if match else u'LiveFootbalLOL',
                    u'Todavía no se han publicado los enlaces del partido',
                    time=5000
                )

            # Si no es un enlace acestream continua
            ch_link = tools.str_sanitize(cells[1].find('a').get('href'))
            if not ch_link or not 'acestream' in ch_name.lower():
                continue

            # Obtiene el idioma
            if not ch_lang or not re.findall(r'(\[[A-Z]{2}\])', ch_lang, re.U):
                ch_lang = prev_lang
            prev_lang = ch_lang

            # Obtiene los datos extendidos y los hashlinks del canal
            channel_data = self.__get_channel_data(cache, ch_link)
            if channel_data:
                for link in channel_data['links']:
                    channels.append(
                        {
                            'name': self.__get_channel_name(
                                channel_data['name'],
                                channel_data['bitrate'],
                                channel_data['signal'],
                                link['hd'],
                                ch_lang),
                            'icon': tools.get_channel_art(self.__settings['path'], channel_data['name']),
                            'fanart': tools.build_path(self.__settings['path'], 'lfol_art.jpg'),
                            'hash': link['hash']
                        }
                    )

        if len(channels) == 0:
            raise WebSiteError(
                u'No hay enlaces',
                u'Los de LiveFootbalLOL han hecho cambios en la Web',
                time=6000
            )

        # Guarda los eventos en caché
        cache.save(event_url, channels)

        return channels

    def __get_channel_data(self, cache, url):
        """
        Get channel data for an URL

        :param url: The channel URL
        :type: url: str
        :return: The Acestream channel data
        :rtype: dict
        """
        # Busca los datos del canal en caché
        channel_data = cache.load(url, True)
        if channel_data:
            return channel_data

        # Los datos del canal no están en cache
        # Vuelve a obtenerlos
        channel_data = {}

        # GET url
        page = tools.get_web_page(url)
        if not page:
            tools.write_log('Error al conectar: ' + url, xbmc.LOGERROR)
            raise WebSiteError(
                u'Error de conexión',
                u'¿Estás conectado a Internet?',
                time=8000
            )

        # Obtiene la tabla de canales
        soup = BeautifulSoup(page, 'html5lib')
        table = soup.find('table', attrs={'class': 'uk-table'})

        # Datos del canal
        ch_name = ''
        ch_sign = ''
        ch_rate = ''
        ch_links = []

        # Obtiene los datos del canal
        for row in table.findAll("tr"):
            cells = row.findAll("td")
            cell_0 = tools.str_sanitize(cells[0].get_text())
            if len(cells) == 2:
                if 'Name' in cell_0:
                    ch_name = tools.str_sanitize(cells[1].get_text())
                elif 'Bitrate' in cell_0:
                    ch_rate = tools.str_sanitize(cells[1].get_text())
                elif 'Signal' in cell_0:
                    ch_sign = tools.str_sanitize(cells[1].get_text())
            elif 'acestream://' in cell_0:
                hashes = re.findall(
                    r'[acestrm:/]*([0-9a-f]{40})', tools.str_sanitize(cells[0].find('a').get('href')), re.U)
                if hashes:
                    ch_links.append({
                        'hash': hashes[0],
                        'hd': '(HD)' in cell_0
                    })

        if len(ch_links) == 0:
            return None

        channel_data = {
            'name': ch_name,
            'bitrate': ch_rate,
            'signal': ch_sign,
            'links': ch_links
        }

        # Guarda los datos del canal en caché
        cache.save(url, channel_data)
        return channel_data

    def __get_channel_name(self, name, bitrate, signal, is_hd, lang):
        color = 'yellow'

        if 'high' == signal.lower():
            color = 'lime'
        elif 'low' == signal.lower():
            color = 'red'

        return '%s %s [COLOR %s]%s(%s)[/COLOR]' % (name, lang, color, '[B](HD)[/B] ' if is_hd else '', bitrate)
