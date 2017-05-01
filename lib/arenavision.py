# -*- coding: utf-8 -*-
import datetime
import re
import tools

import xbmc

from bs4 import BeautifulSoup

from lib import lang, art
from lib.cache import Cache
from lib.errors import WebSiteError


class Arenavision:

    __web_url = 'http://arenavision.in/'

    def __init__(self, settings):
        self.__settings = settings

    def get_menu(self):
        """
        Get the list of Arenavision categories: agenda, sports and competition

        :return: The list of Arenavision categories
        :rtype: list
        """
        return [
            {
                'name': 'Hoy y mañana',
                'icon': tools.build_path(self.__settings['path'], 'hoy_manana.png'),
                'fanart': tools.build_path(self.__settings['path'], 'arenavision_art.jpg')
            }, {
                'name': 'Agenda 7 días',
                'icon': tools.build_path(self.__settings['path'], 'siete_dias.png'),
                'fanart': tools.build_path(self.__settings['path'], 'arenavision_art.jpg')
            }, {
                'name': 'Deportes',
                'icon': tools.build_path(self.__settings['path'], 'deportes.png'),
                'fanart': tools.build_path(self.__settings['path'], 'arenavision_art.jpg')
            }, {
                'name': 'Competiciones',
                'icon': tools.build_path(self.__settings['path'], 'competiciones.png'),
                'fanart': tools.build_path(self.__settings['path'], 'arenavision_art.jpg')
            }]

    def __get_competition_art(self, sport, competition):
        icon = art.get_competition_icon(competition, self.__settings['path'])
        sport_art = art.get_sport_art(sport, self.__settings['path'])
        if icon is None:
            icon = sport_art['icon']
        return {
            'icon': icon,
            'fanart': sport_art['fanart']
        }

    @staticmethod
    def __get_event_name(event, date, time, competition):
        color = 'yellow'
        now = datetime.datetime.now()

        event_date = date.split('/')
        event_time = time.split(':')

        event_dt_start = datetime.datetime(
            int(event_date[2]),
            int(event_date[1]),
            int(event_date[0]),
            int(event_time[0]),
            int(event_time[1])
        )

        # noinspection PyTypeChecker
        if event_dt_start - datetime.timedelta(minutes=5) <= now <= event_dt_start + datetime.timedelta(hours=2):
            color = 'lime'
        elif now >= event_dt_start:
            color = 'orange'

        name = event.split('-')
        name = '%s - %s' % (name[0], name[1]) if len(name) == 2 else event

        return '[COLOR %s](%s %s:%s)[/COLOR] (%s) [B]%s[/B]' % \
               (color, date[:5], event_time[0], event_time[1], lang.translate(competition), name)

    def __get_urls(self, page):
        channels = []
        agenda_url = None
        urls = re.findall(r'href=[\'"]?([^\'" >]+)', page, re.U)
        if not (urls and type(urls) == list and len(urls) > 30):
            return None
        for url in urls:
            if re.search(r'^.*av.*[1-3]?[0-9]\W*$', url, re.U):
                channels.append(url if 'http' in url else '%s%s' % (
                    self.__web_url[:-1] if url.startswith('/') else self.__web_url, url))
            elif 'sc' in url:
                agenda_url = url if 'http' in url else '%s%s' % (
                    self.__web_url[:-1] if url.startswith('/') else self.__web_url, url)
        if agenda_url and len(channels) > 0:
            return {'agenda': agenda_url, 'channels': channels}
        return None

    def get_all_events(self):
        """
        Get all Arenavision events

        :return: The list of Arenavision events
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
                    event['name'] = self.__get_event_name(
                        event['event'], event['date'], event['time'], event['competition']
                    )
                return events

        # La URI de la agenda y los enlaces no están en cache
        # Vuelve a obtener la agenda, los enlaces a los canales y los eventos
        events = []

        # GET arenavision.in
        page = tools.get_web_page(self.__web_url)

        # Averigua la URI de la agenda y los enlaces de los canales
        # buscando en todas las URL de la página principal:
        # 'av*1' para los canales AV1, AV2...
        # 'sc' para la agenda
        urls = self.__get_urls(page)
        if not urls:
            raise WebSiteError(
                u'Agenda no encontrada',
                u'Los de Arenavision han hecho cambios en la Web',
                time=self.__settings['notify_secs']
            )

        # Guarda la URI de la agenda y los enlaces de los canales en caché
        cache.save(self.__web_url, urls)

        # GET agenda
        agenda = tools.get_web_page(urls['agenda'])

        # Obtiene la tabla de eventos
        soup = BeautifulSoup(agenda, 'html5lib')
        table = soup.find('table', attrs={'class': 'auto-style1'})

        for row in table.findAll("tr")[1:-2]:
            cells = row.findAll("td")
            links = self.__get_links(tools.str_sanitize(cells[5].get_text()), urls['channels'])
            if links and len(links) > 0:
                time_e = re.findall(r'([0-2][0-9]:[0-5][0-9])', cells[1].get_text(), re.U)
                time_e = time_e[0] if time_e else '00:00'
                competition_art = self.__get_competition_art(cells[2].get_text(), cells[3].get_text())
                events.append(
                    {
                        'date': tools.str_sanitize(cells[0].get_text()),
                        'time': tools.str_sanitize(time_e),
                        'sport': tools.str_sanitize(cells[2].get_text()),
                        'competition': tools.str_sanitize(cells[3].get_text()),
                        'event': tools.str_sanitize(cells[4].get_text()),
                        'channels': links,
                        'name': self.__get_event_name(
                            tools.str_sanitize(cells[4].get_text()),
                            tools.str_sanitize(cells[0].get_text()),
                            tools.str_sanitize(time_e),
                            tools.str_sanitize(cells[3].get_text())),
                        'icon': competition_art['icon'],
                        'fanart': competition_art['fanart']
                    }
                )

        if len(events) == 0:
            raise WebSiteError(
                u'Problema en la agenda',
                u'No hay eventos, ve a la Web y compruébalo',
                time=self.__settings['notify_secs']
            )

        # Guarda los eventos en caché
        cache.save(urls['agenda'], events)

        return events

    def __get_links(self, channels, urls):
        """
        Get link list of channels URL's for a given string

        :param channels: The channels string
        :type: channels: str
        :return: The list of Arenavision events
        :rtype: list
        """
        ch_list = []
        ch_temp = channels.split(' ')

        if len(ch_temp) < 2:
            tools.write_log('No se pueden extraer los enlaces: ' + str(ch_temp), xbmc.LOGERROR)
            return None

        for x in range(0, len(ch_temp) / 2):
            try:
                numbers = ch_temp[x * 2].split('-')
                lang_code = ch_temp[x * 2 + 1]
                for number in numbers:
                    ch_list.append({
                        'name': 'AV%s %s' % (number, lang_code),
                        'icon': tools.build_path(self.__settings['path'], 'arenavision.jpg'),
                        'fanart': tools.build_path(self.__settings['path'], 'arenavision_art.jpg'),
                        'link': urls[int(number) - 1]
                    })
            except ValueError:
                tools.write_log('Enlaces mal formados: ' + str(ch_temp), xbmc.LOGERROR)
                continue

        return ch_list

    def get_events_today_and_tomorrow(self):
        """
        Get today and tomorrow Arenavision events

        :return: The list of Arenavision events
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

    def get_events_by_sport(self, sport):
        """
        Get Arenavision events by a given sport

        :param sport: The sport name
        :type: sport: str
        :return: The list of Arenavision events
        :rtype: list
        """
        sports = []
        events = self.get_all_events()

        for event in events:
            if event['sport'] == sport:
                sports.append(event)

        return sports

    def get_events_by_competition(self, competition):
        """
        Get Arenavision events by a given competition

        :param competition: The competition name
        :type: competition: str
        :return: The list of Arenavision events
        :rtype: list
        """
        competitions = []
        events = self.get_all_events()
        for event in events:
            if event['competition'] == competition:
                competitions.append(event)
        return competitions

    def get_sports(self):
        sport_events = []
        sports = []
        sports_list = []
        events = self.get_all_events()

        # Lista de deportes en la guía
        for event in events:
            if not event['sport'] in sports:
                sports.append(event['sport'])

        # Construye la lista deportes: añade al título el número de eventos que contiene
        for sport in sports:
            sport_events[:] = []
            sport_art = art.get_sport_art(sport, self.__settings['path'])
            for event in events:
                if event['sport'] == sport:
                    sport_events.append(sport)
            sports_list.append({
                'name': '[B]%s[/B] (%i)' % (lang.translate(sport), len(sport_events)),
                'sport_id': sport,
                'icon': sport_art['icon'],
                'fanart': sport_art['fanart']
            })

        return sports_list

    def get_competitions(self):
        competitions = []
        competition_events = []
        competitions_list = []
        events = self.get_all_events()

        # Lista de competiciones en la guía
        for event in events:
            if not event['competition'] in competitions:
                competitions.append(event['competition'])

        # Construye la lista competiciones: añade al título el número de eventos que contiene
        for competition in competitions:
            competition_events[:] = []
            sport = self.__get_sport(events, competition)
            competition_art = self.__get_competition_art(sport, competition)
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

    @staticmethod
    def __get_sport(events, competition):
        for event in events:
            if event['competition'] == competition:
                return event['sport']

    def get_channels(self, name, date, time):
        """
        Get Arenavision channels by a given event name

        :param name: The event name
        :type: name: str
        :param date: The event date
        :type: date: str
        :param time: The event time
        :type: time: str
        :return: The list of Arenavision event channels
        :rtype: list
        """
        events = self.get_all_events()

        for event in events:
            if name.decode('utf-8') == event['name'] and date == event['date'] and time == event['time']:
                if len(event['channels']) == 0:
                    raise WebSiteError(
                        u'Problema en la agenda',
                        u'No hay enlaces para %s' % event['name'],
                        time=self.__settings['notify_secs'])
                return event['channels']
