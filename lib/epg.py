# -*- coding: utf-8 -*-
import datetime
import json
import re
import time

import tools
from lib import art
from lib.cache import Cache
from lib.errors import WebSiteError


class EPG:

    __channels_epg = 'http://vertele.eldiario.es/programaciontv/'

    __channels = [
        'Formula', 'La 1', 'La 2', 'Antena 3', 'Cuatro', 'Telecinco', 'Sexta', '24', 'Clan', 'Teledeporte', 'Neox', 'Nova',
        'Atres', 'Mega', 'FDF', 'Energy', 'Be Mad', 'Divinity', 'Boing', 'Gol', 'MAX', '13tv', 'Intereconom',
        'Disney Ch', 'TEN', 'Kiss', 'Real Madrid', 'Paramount', 'Telemadrid', 'Otra', 'TV3', '33', 'sport 3',
        'TB 1', 'TB 2', 'TB 3', 'TB 4', 'TVG', 'Canal Sur', 'Andaluc', 'Mancha', 'Arag', 'TPA', 'Extremadura',
        'Estrenos', 'Series', '#0', 'tbol', 'beIN LaLiga', 'beIN Sport', 'AXN', 'Life', 'FOX', 'TNT', 'Nickelodeon',
        'Calle 13', 'Sy', 'Historia', 'Geographic', 'Odis', 'Discovery', 'COSMO', 'Decasa', 'Cocina', 'Viajar',
        'Hollywood', 'Comedy', 'Non Stop', 'Eurosport', 'MTV', 'TCM', 'AMC', 'MotoGP', 'Barca', '8'
    ]

    def __init__(self, settings):
        self.__settings = settings

    def __get_epg_data(self):
        """
        Get a list containing the EPG data
    
        :return: The list containing the EPG data
        :rtype: list
        """
        cache = Cache(self.__settings['path'], minutes=180)

        # Busca la EPG en cache
        epg = cache.load(self.__channels_epg, log_read_ok=False)
        if epg:
            return epg

        # No está en cache, la obtiene
        epg = []

        # GET url
        try:
            page = tools.get_web_page(self.__channels_epg)
        except WebSiteError as e:
            tools.write_log('%s: %s' % (e.title, e.message))
            return epg

        # Busca los datos en formato json
        data = re.findall(r'data-json="(.*)"', page, re.U)
        if not data:
            tools.write_log('data-json= not found in %s' % self.__channels_epg)
            return epg

        # Carga y guarda la EPG
        try:
            epg = json.loads(tools.str_sanitize(data[0]))['channels']
            cache.save(self.__channels_epg, epg)
        except (ValueError, IndexError, KeyError):
            tools.write_log('Malformed data-json= in %s' % self.__channels_epg)

        return epg

    def __get_by_channel_name(self, epg, channel_name):
        for ch_name in self.__channels:
            chn = channel_name.encode('utf-8').lower().replace('ç', 'c').replace(' ', '') \
                if isinstance(channel_name, unicode) \
                else channel_name.decode('utf-8').lower().replace(u'ç', u'c').replace(' ', '')
            if ch_name.lower().replace(' ', '') in chn:
                for data in epg:
                    dch = data['channel'].encode('utf-8')
                    if ch_name in dch.replace('ç', 'c'):
                        return data
        return None

    def add_metadata(self, channels):
        # Obtiene la EPG
        epg = self.__get_epg_data()
        if not epg:
            return channels

        # Añade los datos
        for channel in channels:

            # Añade el logo del canal
            chn = channel['name'].encode('utf-8').lower().replace('ç', 'c').replace(' ', '') \
                if isinstance(channel['name'], unicode) \
                else channel['name'].decode('utf-8').lower().replace(u'ç', u'c').replace(' ', '')
            channel['icon'] = art.get_epg_channel_logo(chn, self.__settings['path'])

            # Busca la EPG del canal
            channel_epg = self.__get_by_channel_name(epg, channel['name'])
            if not channel_epg:
                continue

            # Busca en la EPG del canal el programa que se está emitiendo
            epg_info = self.__get_program_data(channel_epg['events'])
            if not epg_info:
                continue

            # Añade la información al canal
            # Compone el nombre, el icono y plot
            hora = datetime.datetime.fromtimestamp(epg_info['starts']).strftime('%H:%M')
            channel.update(epg_info)

            chnam = channel['name'].encode('utf-8') \
                if isinstance(channel['name'], unicode) \
                else channel['name'].decode('utf-8')
            epgti = epg_info['title'] \
                if isinstance(epg_info['title'], unicode) \
                else epg_info['title'].decode('utf-8')
            try:
                channel['name'] = '%s [COLOR yellow](%s %s)[/COLOR]' % (chnam, hora, epgti)
            except UnicodeDecodeError:
                channel['name'] = '%s [COLOR yellow](%s %s)[/COLOR]' % (chnam, hora, epg_info['title'].encode('utf-8'))

            if epg_info['image'] and epg_info['image'].startswith('http'):
                channel['icon'] = epg_info['image']

            channel['plot'] = '[B]%s %s[/B]%s[CR]Finaliza: %s[CR][CR][LIGHT]%s[/LIGHT]' % (
                hora,
                epg_info['title'].encode('utf-8'),
                ' (%s)' % epg_info['tvshowtitle'].encode('utf-8') if epg_info['tvshowtitle'] else '',
                datetime.datetime.fromtimestamp(epg_info['ends']).strftime('%H:%Mh'),
                epg_info['plot'].encode('utf-8'),
            )

        return channels

    def update_metadata(self, channels):

        # Obtiene la EPG
        epg = self.__get_epg_data()
        if not epg:
            return channels

        # Añade los datos
        tools.write_log('Updating EPG metadata')
        for channel in channels:
            chn = channel['name'].split(' [COLOR ')[0]

            # Busca la EPG del canal
            channel_epg = self.__get_by_channel_name(epg, chn)
            if not channel_epg:
                continue

            # Busca en la EPG del canal el programa que están emitiendo
            epg_info = self.__get_program_data(channel_epg['events'])
            if not epg_info:
                continue

            # Añade la información al canal
            # Compone el nombre, el icono y plot

            hora = datetime.datetime.fromtimestamp(epg_info['starts']).strftime('%H:%M')
            channel.update(epg_info)

            channel['name'] = '%s [COLOR yellow](%s %s)[/COLOR]' % (chn, hora, epg_info['title'])

            if epg_info['image'] and epg_info['image'].startswith('http'):
                channel['icon'] = epg_info['image']

            channel['plot'] = '[B]%s %s[/B]%s[CR]Finaliza: %s[CR][CR][LIGHT]%s[/LIGHT]' % (
                hora,
                epg_info['title'].encode('utf-8'),
                ' (%s)' % epg_info['tvshowtitle'].encode('utf-8') if epg_info['tvshowtitle'] else '',
                datetime.datetime.fromtimestamp(epg_info['ends']).strftime('%H:%Mh'),
                epg_info['plot'].encode('utf-8'),
            )

        return channels

    @staticmethod
    def __get_program_data(epg_programs):
        now = time.time()
        if type(epg_programs) == list:
            for event in epg_programs:
                # noinspection PyTypeChecker
                if event['eventid'] != 0 and float(event['starts']) <= now < float(event['ends']):
                    return {
                        'starts': event['starts'],
                        'ends': event['ends'],
                        'title': event['title'],
                        'tvshowtitle': event['subtitle'],
                        'plot': event['description'],
                        'plotoutline': event['description2'],
                        'genre': event['genre'],
                        'image': event['image'].split('?')[0],
                        'cast': event['actor'].split(', '),
                        'director': event['director'],
                        'credits': event['creator'],
                        'aired': datetime.datetime.fromtimestamp(event['starts']).strftime('%Y-%m-%d'),
                        'duration': str(int(event['duration'] / 60)),
                        'mediatype': 'movie' if 'Cine' in event['genre'] else
                        ('episode' if 'Serie' in event['genre'] else 'tvshow')
                    }
        else:
            tools.write_log('EPG Events type:%s "%s"' % (type(epg_programs), epg_programs))

        return None
