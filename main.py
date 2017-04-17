# -*- coding: utf-8 -*-
import re
import sys

import xbmc
import xbmcaddon

from urlparse import parse_qsl

from lib import tools
from lib.cache import Cache
from lib.errors import WebSiteError
from lib.iptv import MovistarTV
from lib.kodi import Kodi
from lib.arenavision import Arenavision
from lib.livefootballol import LiveFootbalLOL
from lib.livefootballvideo import LiveFootballVideo
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
        'name': 'LiveFootballVideo',
        'icon': tools.build_path(__path__, 'lfv.png'),
        'fanart': tools.build_path(__path__, 'lfv_art.jpg')
    },
    {
        'name': 'LiveFootbalLOL',
        'icon': tools.build_path(__path__, 'lfol.png'),
        'fanart': tools.build_path(__path__, 'lfol_art.jpg')
    },
    {
        'name': 'TorrentTV',
        'icon': tools.build_path(__path__, 'ttv.png'),
        'fanart': tools.build_path(__path__, 'ttv_art.jpg')
    },
    {
        'name': 'MovistarTV',
        'icon': tools.build_path(__path__, 'movistar.png'),
        'fanart': tools.build_path(__path__, 'movistar_art.jpg')
    }
]


# Opciones del addon
def get_addon_settings():
    return {
        'plot': tools.get_addon_setting('plot', s_type=tools.BOOL),
        'adult': tools.get_addon_setting('adult', s_type=tools.BOOL),
        'notify': tools.get_addon_setting('notify', s_type=tools.BOOL),
        'notify_secs': tools.get_addon_setting('notify_secs', s_type=tools.NUM) * 1000,
        'handle': _handle,
        'path': __path__,
        'version': __version__,
        'url': _url
    }


def check_for_updates(notify, notify_secs):
    cache = Cache(__path__, minutes=5)

    # Si está en caché continúa
    c_version = cache.load(_server_addon_xml_url, False)
    if c_version:
        return

    # No está en caché, comprueba la última versión
    xml = tools.get_web_page(_server_addon_xml_url)
    if xml:
        server_v = re.findall(r'version="([0-9]{1,5}\.[0-9]{1,5}\.[0-9]{1,5})"', xml, re.U)
        if server_v and type(server_v) == list and len(server_v) > 0:
            cache.save(_server_addon_xml_url, {'version': server_v[0]})
            sv = server_v[0].split('.')
            lv = __version__.split('.')
            if float('%s.%s' % (sv[0], sv[1])) > float('%s.%s' % (lv[0], lv[1])) or \
                    (float('%s.%s' % (sv[0], sv[1])) == float('%s.%s' % (lv[0], lv[1])) and sv[2] > lv[2]):
                tools.write_log('Server version: %s' % server_v[0])
                tools.write_log('Installed version: %s' % __version__)
                if notify:
                    tools.Notify().notify(
                        u'Acestream Sports',
                        u'Se está actualizando a la versión %s' % server_v[0],
                        disp_time=notify_secs
                    )
                xbmc.executebuiltin("UpdateAddonRepos")
                xbmc.executebuiltin("UpdateLocalAddons")


def controller(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Obtiene las opciones del plugin
    settings = get_addon_settings()

    # Busca actualizaciones
    check_for_updates(settings['notify'], settings['notify_secs'])

    # Kodi: funciones para mostar las listas y los vídeos
    kodi = Kodi(settings)

    # Convierte la cadena de parámetros URL a un diccionario {<parameter>: <value>}
    params = dict(parse_qsl(paramstring))

    # Kodi ha invocado al script sin parámetros: muestra la lista de webs
    if not params:
        kodi.show_menu(_web_pages)
    else:

        # Si no hay source va al menu principal de cada web
        if 'source' not in params:

            if params['page'] == 'Arenavision':
                kodi.show_menu(Arenavision(settings).get_menu(), source=params['page'])

            elif params['page'] == 'LiveFootballVideo':
                kodi.show_menu(LiveFootballVideo(settings).get_menu(), source=params['page'])

            elif params['page'] == 'LiveFootbalLOL':
                kodi.show_menu(LiveFootbalLOL(settings).get_menu(), source=params['page'])

            elif params['page'] == 'TorrentTV':
                kodi.show_menu(TorrentTV(settings).get_menu(), source=params['page'])

            elif params['page'] == 'MovistarTV':
                kodi.show_menu(MovistarTV(settings).get_menu(), source=params['page'])

        # Opciones de Arenavision
        elif params['source'] == 'Arenavision':
            arenavision = Arenavision(settings)
            if params['action'] == 'show':

                # Menú de Arenavisión
                if 'item' in params:

                    if params['item'] == 'Hoy y mañana':
                        kodi.show_menu(
                            arenavision.get_events_today_and_tomorrow(),
                            source=params['source'],
                            show_plot=settings['plot']
                        )

                    elif params['item'] == 'Agenda 7 días':
                        kodi.show_menu(
                            arenavision.get_all_events(),
                            source=params['source'],
                            show_plot=settings['plot']
                        )

                    elif params['item'] == 'Deportes':
                        kodi.show_menu(arenavision.get_sports(), source=params['source'])

                    elif params['item'] == 'Competiciones':
                        kodi.show_menu(arenavision.get_competitions(), source=params['source'])

                # Menú de Deportes
                elif 'sport_id' in params:
                    kodi.show_menu(
                        arenavision.get_events_by_sport(params['sport_id']),
                        source=params['source'],
                        show_plot=settings['plot']
                    )

                # Menú de Competiciones
                elif 'competition_id' in params:
                    kodi.show_menu(
                        arenavision.get_events_by_competition(params['competition_id']),
                        source=params['source'],
                        show_plot=settings['plot']
                    )

                # Menú de Canales AV1, AV2, AV3...
                elif 'event' in params:
                    kodi.show_channels(
                        arenavision.get_channels(params['event'], params['date'], params['time']),
                        source=params['source']
                    )

            # Viene del menú de canales: busca hashlink en url y lo reproduce
            if params['action'] == 'play':
                hashlink = tools.get_hashlink(params['url'], settings)
                Kodi.play_acestream_link(hashlink, params['name'], params['icon'])

        # Opciones de LiveFootballVideo
        elif params['source'] == 'LiveFootballVideo':
            livefootballvideo = LiveFootballVideo(settings)
            if params['action'] == 'show':

                # Menú de LiveFootbalLOL
                if 'item' in params:

                    if params['item'] == 'Hoy y mañana':
                        kodi.show_menu(
                            livefootballvideo.get_events_today_and_tomorrow(),
                            source=params['source'],
                            show_plot=settings['plot']
                        )

                    elif params['item'] == 'Agenda 7 días':
                        kodi.show_menu(
                            livefootballvideo.get_all_events(),
                            source=params['source'],
                            show_plot=settings['plot']
                        )

                    elif params['item'] == 'Competiciones':
                        kodi.show_menu(
                            livefootballvideo.get_competitions(),
                            source=params['source']
                        )

                # Menú de Competiciones
                elif 'competition_id' in params:
                    kodi.show_menu(
                        livefootballvideo.get_events_by_competition(params['competition_id']),
                        source=params['source'],
                        show_plot=settings['plot']
                    )

                # Menú de Canales AV1, Sports1, AV3...
                elif 'event' in params:
                    kodi.show_channels(
                        livefootballvideo.get_channels(params['event']),
                        source=params['source']
                    )

            # Viene del menú de canales: busca hashlink en url y lo reproduce
            if params['action'] == 'play':
                hashlink = tools.get_hashlink(params['url'], settings)
                Kodi.play_acestream_link(hashlink, params['name'], params['icon'])

        # Opciones de LiveFootbalLOL
        elif params['source'] == 'LiveFootbalLOL':
            livefootballol = LiveFootbalLOL(settings)
            if params['action'] == 'show':

                # Menú de LiveFootbalLOL
                if 'item' in params:

                    if params['item'] == 'Hoy y mañana':
                        kodi.show_menu(
                            livefootballol.get_events_today_and_tomorrow(),
                            source=params['source'],
                            show_plot=settings['plot']
                        )

                    elif params['item'] == 'Agenda 7 días':
                        kodi.show_menu(
                            livefootballol.get_all_events(),
                            source=params['source'],
                            show_plot=settings['plot']
                        )

                    elif params['item'] == 'Competiciones':
                        kodi.show_menu(
                            livefootballol.get_competitions(),
                            source=params['source']
                        )

                # Menú de Competiciones
                elif 'competition_id' in params:
                    kodi.show_menu(
                        livefootballol.get_events_by_competition(params['competition_id']),
                        source=params['source'],
                        show_plot=settings['plot']
                    )

                # Menú de Canales AV1, AV2, Match TV HD...
                elif 'event' in params:
                    kodi.show_channels(livefootballol.get_channels(params['event']))

        # Opciones de TorrentTV
        elif params['source'] == 'TorrentTV':
            torrenttv = TorrentTV(settings)
            if params['action'] == 'show':

                # Menú de TorrentTV
                if 'category_id' in params:
                    kodi.show_channels(
                        torrenttv.get_channels_by_category(params['category_id']),
                        show_plot=settings['plot']
                    )

        # Opciones de MovistarTV
        elif params['source'] == 'MovistarTV':
            movistartv = MovistarTV(settings)
            if params['action'] == 'show':

                # Menú de MovistarTV
                if 'event' in params:
                    kodi.show_channels(movistartv.get_channels(params['event']))

        elif params['action'] == 'play':
            if 'url' in params:
                Kodi.play_acestream_link(params['url'], params['name'], params['icon'])
            elif 'video' in params:
                kodi.play_video(params['video'])


if __name__ == '__main__':
    try:
        # Llama al controlador y le pasa la cadena de parámetros
        controller(sys.argv[2][1:])
    except WebSiteError as e:
        tools.write_log('%s: %s' % (e.title, e.message))
        tools.Notify().notify(e.title, e.message, disp_time=e.time)
