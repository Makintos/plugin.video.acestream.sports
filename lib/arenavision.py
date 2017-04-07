# -*- coding: utf-8 -*-
import datetime
import re
import tools

import xbmc

from bs4 import BeautifulSoup
from lib.cache import Cache


class Arenavision:

    __agenda_url = 'http://arenavision.in/schedule'
    __channel_url = 'http://arenavision.in/av%s'

    __translations = {
        'SOCCER': 'Fútbol',
        'BASKETBALL': 'Baloncesto',
        'FORMULA 1': 'Formula 1',
        'MOTOGP': 'Moto GP',
        'TENNIS': 'Tenis',
        'MMA': 'Lucha',
        'CYCLING': 'Ciclismo',
        'FOOTBALL': 'Football americano',
        'BASEBALL': 'Beisbol',
        'VOLLEYBALL': 'Voleybol',
        'GOLF': 'Golf',
        'HOCKEY': 'Hockey',
        'RUGBY': 'Rugby',
        'USA NBA': 'NBA',
        'URUGUAY LEAGUE': 'Liga Uruguaya',
        'COPA SUDAMERICANA': 'Copa Sudamericana',
        'COLOMBIA PRIMERA': 'Liga Colombiana',
        'MEXICO COPA MX': 'Copa de Mexico',
        'MEXICO LIGA MX': 'Liga Mexicana',
        'SPANISH LA LIGA': 'La Liga',
        'SPANISH LA LIGA 2': 'La Liga 123',
        'EUROLEAGUE': 'Euroliga',
        'PORTUGAL A LIGA': 'Liga Portuguesa',
        'CHILE LEAGUE': 'Liga Chilena',
        'DAVIS CUP': 'Davis CUP',
        'FRENCH LIGUE 1': 'Liga Francesa',
        'ITALY SERIE A': 'Liga Italiana',
        'PREMIER LEAGUE': 'Liga Inglesa',
        'BUNDESLIGA': 'Liga Alemana',
        'SPANISH ACB': 'Liga ACB',
        'USA MLS': 'Liga de USA'
    }

    def __build_thumbs(self):
        self.__sport_art = {
            'SOCCER': {
                'icon': tools.build_path(self.__path, 'futbol.png'),
                'fanart': tools.build_path(self.__path, 'futbol_art.jpg')
            },
            'BASKETBALL': {
                'icon': tools.build_path(self.__path, 'basket.png'),
                'fanart': tools.build_path(self.__path, 'basket_art.jpg')
            },
            'FORMULA 1': {
                'icon': tools.build_path(self.__path, 'f1.png'),
                'fanart': tools.build_path(self.__path, 'f1_art.jpg')
            },
            'MOTOGP': {
                'icon': tools.build_path(self.__path, 'motogp.png'),
                'fanart': tools.build_path(self.__path, 'motogp_art.jpg')
            },
            'TENNIS': {
                'icon': tools.build_path(self.__path, 'tenis.png'),
                'fanart': tools.build_path(self.__path, 'tenis_art.jpg')
            },
            'MMA': {
                'icon': tools.build_path(self.__path, 'mma.png'),
                'fanart': tools.build_path(self.__path, 'mma_art.jpg')
            },
            'CYCLING': {
                'icon': tools.build_path(self.__path, 'ciclismo.png'),
                'fanart': tools.build_path(self.__path, 'ciclismo_art.jpg')
            },
            'FOOTBALL': {
                'icon': tools.build_path(self.__path, 'rugby.png'),
                'fanart': tools.build_path(self.__path, 'rugby_art.jpg')
            },
            'BASEBALL': {
                'icon': tools.build_path(self.__path, 'baseball.png'),
                'fanart': tools.build_path(self.__path, 'baseball_art.jpg')
            },
            'VOLLEYBALL': {
                'icon': tools.build_path(self.__path, 'voley.png'),
                'fanart': tools.build_path(self.__path, 'voley_art.jpg')
            },
            'GOLF': {
                'icon': tools.build_path(self.__path, 'golf.png'),
                'fanart': tools.build_path(self.__path, 'golf_art.jpg')
            },
            'HOCKEY': {
                'icon': tools.build_path(self.__path, 'hockey.png'),
                'fanart': tools.build_path(self.__path, 'hockey_art.jpg')
            },
            'RUGBY': {
                'icon': tools.build_path(self.__path, 'rugby.png'),
                'fanart': tools.build_path(self.__path, 'rugby_art.jpg')
            }
        }
        self.__competition_thumbs = {
            'FRENCH CUP': tools.build_path(self.__path, 'liga_fr.png'),
            'SPANISH LA LIGA': tools.build_path(self.__path, 'liga_es_1.png'),
            'BUNDESLIGA': tools.build_path(self.__path, 'liga_de_1.png'),
            'ITALIA CUP': tools.build_path(self.__path, 'liga_it.png'),
            'PREMIER LEAGUE': tools.build_path(self.__path, 'liga_en.png'),
            'PORTUGAL CUP': tools.build_path(self.__path, 'liga_po.png'),
            'USA NBA': tools.build_path(self.__path, 'nba.png'),
            'USA MLS': tools.build_path(self.__path, 'liga_usa_mls.png'),
            'MEXICO LIGA MX': tools.build_path(self.__path, 'liga_mx.png'),
            'MEXICO COPA MX': tools.build_path(self.__path, 'copa_mx.png'),
            'COPA SUDAMERICANA': tools.build_path(self.__path, 'copa_sudamerica.png'),
            'CONCACAF CHAMPIONS LEAGUE': tools.build_path(self.__path, 'liga_concaf.jpg'),
            'URUGUAY LEAGUE': tools.build_path(self.__path, 'liga_ur.png'),
            'COLOMBIA PRIMERA': tools.build_path(self.__path, 'liga_col.png'),
            'EUROLEAGUE': tools.build_path(self.__path, 'euroliga.png'),
            'SPANISH LA LIGA 2': tools.build_path(self.__path, 'liga_es_2.png'),
            'FRENCH LIGUE 1': tools.build_path(self.__path, 'liga_fr.png'),
            'CHILE LEAGUE': tools.build_path(self.__path, 'liga_ch.png'),
            'ITALY SERIE A': tools.build_path(self.__path, 'liga_it_serie_a.png'),
            'PORTUGAL A LIGA': tools.build_path(self.__path, 'liga_po.png'),
            'SPANISH ACB': tools.build_path(self.__path, 'liga_acb.png'),
        }

    def __init__(self, path):
        self.__path = path
        self.__build_thumbs()

    def get_menu(self):
        """
        Get the list of Arenavision categories: agenda, sports and competition

        :return: The list of Arenavision categories
        :rtype: list
        """
        return [
            {
                'name': 'Hoy y mañana',
                'icon': tools.build_path(self.__path, 'hoy_manana.png'),
            }, {
                'name': 'Agenda 7 días',
                'icon': tools.build_path(self.__path, 'siete_dias.png'),
            }, {
                'name': 'Deportes',
                'icon': tools.build_path(self.__path, 'deportes.png'),
            }, {
                'name': 'Competiciones',
                'icon': tools.build_path(self.__path, 'competiciones.png'),
            }]

    def __get_competition_art(self, sport, competition):
        icon = self.__competition_thumbs.get(tools.str_sanitize(competition).upper(), None)
        sport_art = self.__get_sport_art(sport)
        if icon is None:
            icon = sport_art['icon']
        return {
            'icon': icon,
            'fanart': sport_art['fanart']
        }

    def __get_sport_art(self, sport):
        return self.__sport_art.get(tools.str_sanitize(sport).upper(), {
            'icon': tools.build_path(self.__path, 'sports.png'),
            'fanart': tools.build_path(self.__path, 'sports_art.jpg')
        })

    def __get_event_name(self, event, date, time, competition):
        color = 'yellow'
        now = datetime.datetime.now()

        event_date = date.split('/')
        event_time = time.split(':')

        if now >= datetime.datetime(
                int(event_date[2]), int(event_date[1]), int(event_date[0]), int(event_time[0]), int(event_time[1])):
            color = 'orange'

        name = event.split('-')
        name = '%s - %s' % (name[0], name[1]) if len(name) == 2 else event

        return '[COLOR %s](%s %s:%s)[/COLOR] (%s) [B]%s[/B]' % \
               (color, date[:5], event_time[0], event_time[1], self.__translations.get(competition, competition), name)

    def get_all_events(self):
        """
        Get all Arenavision events

        :return: The list of Arenavision events
        :rtype: list
        """
        cache = Cache(self.__path)

        # Busca la agenda en cache
        events = cache.load(self.__agenda_url)
        if events:
            return events

        # No está en cache, la obtiene
        events = []
        page = tools.get_web_page(self.__agenda_url)

        if not page:
            return events

        soup = BeautifulSoup(page, 'html5lib')
        table = soup.find('table', attrs={'class': 'auto-style1'})

        for row in table.findAll("tr")[1:-2]:
            cells = row.findAll("td")
            links = self.__get_links(tools.str_sanitize(cells[5].get_text()))
            if links and len(links) > 0:
                art = self.__get_competition_art(cells[2].get_text(), cells[3].get_text())
                events.append(
                    {
                        'date': tools.str_sanitize(cells[0].get_text()),
                        'time': tools.str_sanitize(cells[1].get_text()[:5]),
                        'sport': tools.str_sanitize(cells[2].get_text()),
                        'competition': tools.str_sanitize(cells[3].get_text()),
                        'event': tools.str_sanitize(cells[4].get_text()),
                        'channels': links,
                        'name': self.__get_event_name(
                            tools.str_sanitize(cells[4].get_text()),
                            tools.str_sanitize(cells[0].get_text()),
                            tools.str_sanitize(cells[1].get_text()[:5]),
                            tools.str_sanitize(cells[3].get_text())),
                        'icon': art['icon'],
                        'fanart': art['fanart']
                    }
                )
        cache.save(self.__agenda_url, events)
        return events

    def __get_links(self, channels):
        """
        Get channel links list for a given event

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
            numbers = ch_temp[x * 2].split('-')
            lang = ch_temp[x * 2 + 1]
            for number in numbers:
                ch_list.append({
                    'name': 'AV%s %s' % (number, lang),
                    'icon': tools.build_path(self.__path, 'arenavision.jpg'),
                    'fanart': tools.build_path(self.__path, 'arenavision_art.jpg'),
                    'link': self.__channel_url % number
                })

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
            sport_art = self.__get_sport_art(sport)
            for event in events:
                if event['sport'] == sport:
                    sport_events.append(sport)
            sports_list.append({
                'name': '[B]%s[/B] (%i)' % (self.__translations.get(sport, sport), len(sport_events)),
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
            art = self.__get_competition_art(sport, competition)
            for event in events:
                if event['competition'] == competition:
                    competition_events.append(competition)
            competitions_list.append({
                'name': '[B]%s[/B] (%i)' % (self.__translations.get(competition, competition), len(competition_events)),
                'competition_id': competition,
                'icon': art['icon'],
                'fanart': art['fanart']
            })

        return competitions_list

    def __get_sport(self, events, competition):
        for event in events:
            if event['competition'] == competition:
                return event['sport']

    def get_event_links(self, event_name, event_date, event_time):
        """
        Get Arenavision event links by a given event name

        :param event_name: The event name
        :type: event_name: str
        :return: The list of Arenavision event links
        :rtype: list
        """
        channels = []
        cache = Cache(self.__path, minutes=10)
        events = self.get_all_events()

        for event in events:
            if event_name == event['name'] and event_date == event['date'] and event_time == event['time']:
                for channel in event['channels']:
                    # Busca el hash en cache
                    c_hash = cache.load(channel['link'])
                    if c_hash:
                        ace_hash = c_hash['hash']
                    # No está en cache, lo obtiene
                    else:
                        page = tools.get_web_page(channel['link'])
                        ace_hash = re.search(r'.*loadPlayer\(\"([a-f0-9]{40})\",.*', page, re.U).groups()[0]
                        cache.save(channel['link'], {"hash": ace_hash})
                    if ace_hash:
                        channel['hash'] = ace_hash
                        channels.append(channel)
                    else:
                        tools.write_log("Enlace de acestream no encontrado: '%s' de '%s' a las %s del %s" %
                                        (channel['name'], event['event'], event['time'], event['date']), xbmc.LOGERROR)

        return channels
