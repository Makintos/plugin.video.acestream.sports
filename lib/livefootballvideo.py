# -*- coding: utf-8 -*-
import datetime
import re

import xbmc
from bs4 import BeautifulSoup

import tools
from lib import lang, art
from lib.arenavision import Arenavision
from lib.cache import Cache
from lib.errors import WebSiteError


class LiveFootballVideo:

    __web_url = 'http://livefootballvideo.com/'

    def __init__(self, settings):
        self.__settings = settings

    def get_menu(self):
        """
        Get the list of LiveFootballVideo categories: agenda and competitions

        :return: The list of LiveFootballVideo categories
        :rtype: list
        """
        return [
            {
                'name': 'Hoy y mañana',
                'icon': tools.build_path(self.__settings['path'], 'hoy_manana.png'),
                'fanart': tools.build_path(self.__settings['path'], 'lfv_art.jpg')
            }, {
                'name': 'Agenda 7 días',
                'icon': tools.build_path(self.__settings['path'], 'siete_dias.png'),
                'fanart': tools.build_path(self.__settings['path'], 'lfv_art.jpg')
            }, {
                'name': 'Competiciones',
                'icon': tools.build_path(self.__settings['path'], 'competiciones.png'),
                'fanart': tools.build_path(self.__settings['path'], 'lfv_art.jpg')
            }]

    def __get_competition_art(self, competition):
        return {
            'icon': art.get_competition_icon(competition, self.__settings['path'], default='futbol.png'),
            'fanart': tools.build_path(self.__settings['path'], 'futbol_art.jpg')
        }

    @staticmethod
    def __get_event_name(event):
        color = 'yellow'

        now = datetime.datetime.now()
        start = datetime.datetime.fromtimestamp(event['start'])
        end = datetime.datetime.fromtimestamp(event['end'])

        # noinspection PyTypeChecker
        if start - datetime.timedelta(minutes=5) <= now <= end:
            color = 'lime'
        elif now >= start:
            color = 'orange'

        return '[COLOR %s](%s %s)[/COLOR] (%s) [B]%s - %s[/B]' % (
            color,
            start.strftime('%d/%m'),
            start.strftime('%H:%M'),
            lang.translate(event['competition']),
            tools.str_sanitize(event['team1']),
            tools.str_sanitize(event['team2'])
        )

    @staticmethod
    def __get_number_of_pages(page):
        pages = re.findall(r'>[Pp][Aa][Gg][Ee]\s[0-9]+\sof\s([0-9]+)<', page, re.U)
        if not pages:
            tools.write_log(u'LiveFootballVideo: No se encuentra el número de páginas')
            return None
        return int(pages[0])

    def get_all_events(self):
        """
        Get all LiveFootballVideo events

        :return: The list of LiveFootballVideo events
        :rtype: list
        """
        cache = Cache(self.__settings['path'])
        agenda_url = '%sstreaming' % self.__web_url

        # Busca los eventos en cache
        events = cache.load(agenda_url)
        if events:
            for event in events:
                event['name'] = self.__get_event_name(event)
            return events

        # Los eventos no están en cache, vuelve a obtenerlos
        web_events = []
        events = []

        # GET livefootballvideo.com/streaming
        page = tools.get_web_page(agenda_url)

        # Obtiene el número de páginas de la agenda
        total_pages = self.__get_number_of_pages(page)
        if not total_pages:
            total_pages = 1

        # Obtiene la tabla de eventos
        for page_number in range(0, total_pages):
            # GET livefootballvideo.com/streaming/page/{page_number}
            page = tools.get_web_page('%s/page/%i' % (agenda_url, page_number + 1)) if page_number > 0 else page
            e = re.findall(
                '<li\s*(?:class="odd")?>\s*<div\s*class="leaguelogo\s*column">\s*<img.+?src=".+?"\s*alt=".+?"/>' +
                '\s*</div>\s*<div\s*class="league\s*column">\s*<a\s*href=".+?"\s*title=".+?">(.+?)</a>\s*</div>' +
                '\s*<div\s*class="date_time\s*column"><span\s*class="starttime\s*time"\s*rel="(.+?)">.+?</span>' +
                '\s*-\s*<span\s*class="endtime\s*time"\s*rel="(.+?)">.+?</span></div>\s*<div\s*class="team' +
                '\s*column"><img.+?alt="(.+?)"\s*src=".+?"><span>.+?</span></div>\s*<div\s*class="versus' +
                '\s*column">vs.</div>\s*<div\s*class="team\s*away\s*column"><span>(.+?)</span><img.+?alt=".+?"' +
                '\s*src=".+?"></div>\s*<div\s*class="live_btn\s*column">\s*<a\s*(class="online")?\s*href="(.+?)">',
                page)
            if e:
                web_events.extend(map(list, e))

        if len(web_events) == 0:
            raise WebSiteError(
                u'Problema en la agenda',
                u'No hay eventos, puedes comprobarlo en la Web',
                time=self.__settings['notify_secs']
            )

        for event in web_events:
            competition = tools.str_sanitize(event[0])
            competition_art = self.__get_competition_art(event[0])
            start = float(tools.str_sanitize(event[1]))
            end = float(tools.str_sanitize(event[2]))
            team1 = tools.str_sanitize(event[3])
            team2 = tools.str_sanitize(event[4])
            events.append(
                {
                    'start': start,
                    'end': end,
                    'date': datetime.datetime.fromtimestamp(start).strftime('%d/%m/%y'),
                    'time': datetime.datetime.fromtimestamp(start).strftime('%H:%M'),
                    'competition': competition,
                    'team1': team1,
                    'team2': team2,
                    'channel_url': tools.str_sanitize(event[6]),
                    'name': self.__get_event_name(
                        {
                            'start': start,
                            'end': end,
                            'competition': competition,
                            'team1': team1,
                            'team2': team2
                        }),
                    'icon': competition_art['icon'],
                    'fanart': competition_art['fanart']
                }
            )

        if len(events) == 0:
            raise WebSiteError(
                u'Problema en la agenda',
                u'Está vacía o no hay enlaces, puedes comprobarlo en la Web',
                time=self.__settings['notify_secs']
            )

        # Guarda los eventos en caché
        cache.save(agenda_url, events)

        return events

    def get_events_today_and_tomorrow(self):
        """
        Get today and tomorrow LiveFootballVideo events

        :return: The list of LiveFootballVideo events
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
        Get LiveFootballVideo events by a given competition

        :param competition: The competition name
        :type: competition: str
        :return: The list of LiveFootballVideo events
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
                'name': '[B]%s[/B] (%i)' % (lang.translate(competition), len(competition_events)),
                'competition_id': competition,
                'icon': competition_art['icon'],
                'fanart': competition_art['fanart']
            })

        return competitions_list

    def get_channels(self, event_url):
        """
        Get LiveFootballVideo channels by a given event URL

        :param event_url: The event URL
        :type: event_url: str
        :return: The list of LiveFootballVideo event links
        :rtype: list
        """
        cache = Cache(self.__settings['path'], minutes=10)

        # Busca los canales del evento en caché
        channels = cache.load(event_url, True)
        if channels:
            return channels

        # Los datos de los canales no están en cache
        # Vuelve a obtenerlos
        channels = []

        # GET event_url
        page = tools.get_web_page(event_url)

        # Obtiene el bloque que contiene la tabla de enlaces acestream
        soup = BeautifulSoup(page, 'html5lib')
        div = soup.find('div', attrs={'id': 'livelist'})
        if not div:
            raise WebSiteError(
                u'No hay enlaces',
                u'Los de LiveFootballVideo han hecho cambios en la Web',
                time=self.__settings['notify_secs']
            )

        # Obtiene la tabla de datos de los canales
        table = div.find('table', attrs={'class': 'streamtable'})
        if not table:
            # No hay enlaces
            match = re.findall(r'class="thick">(.*)</h3>', page, re.U)
            raise WebSiteError(
                u'%s - %s' % (match[0], match[1]) if match else u'LiveFootballVideo.com',
                u'El partido ya ha terminado, no hay enlaces' if re.findall(r'game was ended', page, re.U) else
                u'Todavía no se han publicado los enlaces del partido',
                time=self.__settings['notify_secs']
            )

        # Obtiene los datos de los canales
        for row in table.findAll("tr")[1:-1]:
            cells = row.findAll("td")

            # Datos del canal
            ch_name = tools.str_sanitize(cells[1].get_text())
            ch_type = tools.str_sanitize(cells[0].find('a').get('title'))
            ch_lang = tools.str_sanitize(cells[2].get_text())
            ch_rate = tools.str_sanitize(cells[3].get_text())
            ch_link = tools.str_sanitize(cells[4].find('a').get('href'))

            if ch_link.startswith('http://arenavision.'):
                ch_link = '%s%s' % (Arenavision.web_url, re.findall(r'http://.*/([0-3][0-9]).*', ch_link, re.U)[0])

            # Si no es un enlace acestream continua
            if not tools.str_sanitize(ch_type).lower() == 'acestream' and 'acestream' not in ch_link:
                continue

            # Prepara el idioma
            ch_lang = '--' if not ch_lang or '-' in ch_lang else ch_lang

            # Prepara el bitrate
            ch_rate = 'desconocido' if not ch_rate or '-' in ch_rate else ch_rate

            channels.append(
                {
                    'name': self.__get_channel_name(ch_name, ch_rate, ch_lang),
                    'icon': art.get_channel_icon(ch_name, self.__settings['path']),
                    'fanart': tools.build_path(self.__settings['path'], 'lfv_art.jpg'),
                    'link': ch_link
                }
            )

        if len(channels) == 0:
            match = re.findall(r'class="thick">(.*)</h3>', page, re.U)
            raise WebSiteError(
                u'%s - %s' % (match[0], match[1]) if match else u'LiveFootballVideo.com',
                u'Hay enlaces del partido pero no son de acestream. Inténtalo más tarde...',
                time=self.__settings['notify_secs']
            )

        # Guarda los eventos en caché
        cache.save(event_url, channels)

        return channels

    @staticmethod
    def __get_channel_name(name, bitrate, lang_code):
        color = 'yellow'

        kbps = bitrate.split(' ')[0]

        if not kbps.isdigit():
            color = 'silver'
        elif int(kbps) >= 2000:
            color = 'lime'
        elif int(kbps) < 1000:
            color = 'red'

        return '%s [%s] [COLOR %s](%s)[/COLOR]' % (name, lang_code, color, bitrate)
