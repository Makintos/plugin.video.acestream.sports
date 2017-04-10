# -*- coding: utf-8 -*-
import re
import sys

import xbmc
import xbmcaddon

from urlparse import parse_qsl

from lib import tools
from lib.cache import Cache
from lib.kodi import Kodi
from lib.arenavision import Arenavision
from lib.torrenttv import TorrentTV

__addon__ = xbmcaddon.Addon()
__version__ = __addon__.getAddonInfo('version')
__path__ = __addon__.getAddonInfo('path')
__lang__ = __addon__.getLocalizedString


# Plugin url (plugin://)
_url = sys.argv[0]

# Plugin handle
_handle = int(sys.argv[1])

# Server addon.xml
_server_addon_xml_url = \
    'https://raw.githubusercontent.com/Makintos/repository.makintos/master/plugin.video.acestream.sports/addon.xml'


_web_pages = [
    {
        'name': 'Arenavision',
        'icon': tools.build_path(__path__, 'arenavision.jpg'),
        'fanart': tools.build_path(__path__, 'arenavision_art.jpg')
    },
    {
        'name': 'TorrentTV',
        'icon': tools.build_path(__path__, 'ttv.png'),
        'fanart': tools.build_path(__path__, 'ttv_art.jpg')
    }
]


def check_for_updates():
    cache = Cache(__path__, minutes=5)

    # Si está en caché no muestro notificación
    c_version = cache.load(_server_addon_xml_url, False)
    if c_version:
        return

    # No está en caché, la obtiene
    xml = tools.get_web_page(_server_addon_xml_url)
    if xml:
        server_v = re.findall(r'version="([0-9]{1,5}\.[0-9]{1,5}\.[0-9]{1,5})"', xml, re.U)
        if server_v and type(server_v) == list and len(server_v) > 0:
            cache.save(_server_addon_xml_url, {'version': server_v[0]})
            sv = server_v[0].split('.')
            lv = __version__.split('.')
            if float('%s.%s' % (sv[0], sv[1])) > float('%s.%s' % (lv[0], lv[1])) or \
                    (float('%s.%s' % (sv[0], sv[1])) == float('%s.%s' % (lv[0], lv[1])) and
                     sv[2] > lv[2]):
                tools.write_log('Server version: %s' % server_v[0])
                tools.write_log('Installed version: %s' % __version__)
                tools.Notify().notify(u'Acestream Sports', u'Actualizando a la versión %s' % server_v[0])
                xbmc.executebuiltin("UpdateAddonRepos")
                xbmc.executebuiltin("UpdateLocalAddons")


def controller(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Busca actualizaciones
    check_for_updates()

    # Kodi: funciones para mostar las listas y los vídeos
    kodi = Kodi(_url, _handle)

    # Convierte la cadena de parámetros URL a un diccionario {<parameter>: <value>}
    params = dict(parse_qsl(paramstring))

    # Kodi ha invocado al script sin parámetros: muestra la lista de webs
    if not params:
        kodi.show_menu(_web_pages)

    # Hay parámetros: muestra el menú o la lista de enlaces/canales correspondiente
    else:

        # Crea los objetos y lanza el menu de la web (viene en params['page'])
        if 'source' not in params:
            exec "%s = %s('%s')" % (params['page'].lower(), params['page'], __path__)
            exec "kodi.show_menu(%s.get_menu(), source='%s')" % (params['page'].lower(), params['page'])

        # Opciones de Arenavision
        elif params['source'] == 'Arenavision':
            arenavision = Arenavision(__path__)
            if params['action'] == 'show':
                if 'item' in params:
                    events = []
                    if params['item'] == 'Hoy y mañana':
                        events = arenavision.get_events_today_and_tomorrow()
                    elif params['item'] == 'Agenda 7 días':
                        events = arenavision.get_all_events()
                    elif params['item'] == 'Deportes':
                        events = arenavision.get_sports()
                    elif params['item'] == 'Competiciones':
                        events = arenavision.get_competitions()
                    kodi.show_menu(events, source=params['source'])
                elif 'event' in params:
                    links = arenavision.get_event_links(params['event'], params['date'], params['time'])
                    kodi.show_events(links)
                elif 'sport_id' in params:
                    events = arenavision.get_events_by_sport(params['sport_id'])
                    kodi.show_menu(events, source=params['source'])
                elif 'competition_id' in params:
                    events = arenavision.get_events_by_competition(params['competition_id'])
                    kodi.show_menu(events, source=params['source'])

        # Opciones de TorrentTV
        elif params['source'] == 'TorrentTV':
            torrenttv = TorrentTV(__path__)
            if params['action'] == 'show':
                if 'category_id' in params:
                    events = torrenttv.get_events_by_category(params['category_id'])
                    kodi.show_events(events)

        elif params['action'] == 'play':
            kodi.play_acestream_link(params['url'], params['name'], params['icon'])


if __name__ == '__main__':
    # Llama al router y le pasa la cadena de parámetros
    # Slicing para eliminar la '?' de los parámetros
    controller(sys.argv[2][1:])
