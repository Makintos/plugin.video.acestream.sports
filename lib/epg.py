# -*- coding: utf-8 -*-
import datetime
import json
import re
import time

import tools
from lib.cache import Cache


class EPG:

    __channels_epg = 'http://vertele.eldiario.es/programaciontv/'

    __channel_names = [
        'la 1 madrid', 'la 1 catalunya', 'la 2 madrid', 'la 2 catalunya', 'la 1', 'la 2', 'antena 3',
        'cuatro', 'telecinco', 'la sexta', '24', 'clan', 'teledeporte', 'neox', 'nova', 'atres', 'mega',
        'fdf', 'energy', 'be mad', 'divinity', 'boing', 'gol', 'max', '13 tv', 'intereconom', 'disney',
        'kiss', 'real madrid', 'paramount', 'tele madrid', 'la otra', 'tv 3', 'canal sur', 'andaluc',
        'tb 1', 'tb 2', 'tvg', 'tvg 2', 'mancha', 'clm', 'arag', 'tpa', 'extremadura', 'cyl', 'estrenos',
        'series', '#0', 'tbol', 'bein la liga', 'bein sports', 'bein', 'fox life', 'fox', 'axn', 'tnt',
        'nickelodeon', 'nick jr', 'nick', 'calle 13', 'syfy', 'sy', 'fy', 'historia', 'geographic',
        'geo', 'odisea', 'odis', 'discovery', 'cosmo', 'decasa', 'cocina', 'viajar', 'hollywood', 'comedy',
        'euro sport 2', 'euro sport', 'mtv', 'tcm', 'amc', 'rmula', 'moto gp', 'barca', 'canal sur 2',
        'canal sur', 'sur', 'tb 3', 'tb 4', 'valencia', 'valenciana', 'murcia', 'navarra', 'ten'
    ]

    def __init__(self, settings):
        self.__settings = settings

    def get_epg_data(self, channel):
        """
        Get a dict containing the EPG data for a given channel
    
        :return: The dict containing icon and fanart for a given category
        :rtype: dict
        """
        # TODO: El tiempo no son 30 min sino hasta las 6:30h del mismo o próximo día, depende de la hora que sea
        # o mejor: hasta el timestamp de fin de uno de los eventos de algún canal de la guia
        cache = Cache(self.__settings['path'], minutes=30)

        # Busca los canales en cache
        epg = cache.load(self.__channels_epg, log_read_ok=False)
        if not epg:
            # No están en cache, los obtiene
            epg = {}

            # GET url
            page = tools.get_web_page(self.__channels_epg)
            if not page:
                tools.write_log('GET 404 %s' % self.__channels_epg)
                return epg

            # Busca los datos json
            data = re.findall(r'data-json="(.*)"', page, re.U)
            if not data:
                tools.write_log('data-json= not found in %s' % self.__channels_epg)
                return epg

            # Carga la EPG
            try:
                epg = json.loads(data[0].encode('utf-8').replace('&quot;', '"').replace('\\/', '/'))['channels']
                cache.save(self.__channels_epg, epg)
            except (ValueError, IndexError, KeyError):
                tools.write_log('Malformed data-json= in %s' % self.__channels_epg)
                return epg

        # Obtiene la EPG para channel
        channel_name = {}

        # Busca en __channel_names el canal 'channel'
        for ch_name in self.__channel_names:
            channel_s = channel.lower().replace('ç', 'c').replace(' ', '')
            ch_name_s = ch_name.lower().replace('ç', 'c').replace(' ', '')
            if ch_name_s in channel_s or channel_s in ch_name_s:
                channel_name = ch_name

        if not channel_name:
            # tools.write_log("EPG channel mapping for '%s' not possible" % channel.decode('utf-8'))
            return channel_name

        data = self.__get_program_data(epg, channel_name)
        if not data:
            tools.write_log("No EPG events/programs for '%s'" % channel.decode('utf-8'))

        return data

    @staticmethod
    def __get_program_data(epg, channel_name):
        for epg_entry in epg:
            if 'channel' in epg_entry and channel_name in epg_entry['channel'] and \
                    type(epg_entry['events']) == list and len(epg_entry['events']) > 0:
                now = time.time()
                for event in epg_entry['events']:
                    # noinspection PyTypeChecker
                    if event['eventid'] != 0 and float(event['starts']) <= now <= float(event['ends']):
                        start = datetime.datetime.fromtimestamp(event['starts'])
                        return {
                            'channel': epg_entry['channel'],
                            'channel_icon': epg_entry['icon'],
                            'starts': event['starts'],
                            'ends': event['ends'],
                            'title': '%s [COLOR yellow](%s %s)[/COLOR]' % (
                                channel_name,
                                start.strftime('%H:%M'),
                                event['title'].encode('utf-8')),
                            'tvshowtitle': event['subtitle'],
                            'plot': event['description'],
                            'plotoutline': event['description2'],
                            'genre': event['genre'],
                            'image': event['image'][:-17],
                            'cast': event['actor'].split(', '),
                            'director': event['director'],
                            'credits': event['creator'],
                            'aired': start.strftime('%Y-%m-%d'),
                            'duration': str(int(event['duration'] / 60)),
                            'mediatype': 'movie' if 'Cine' in event['subtitle'] else 'tvshow'
                        }

            elif type(epg_entry['events']) == dict:
                tools.write_log("EPG Events type:dict in %s" % epg_entry['channel'])

        return None
