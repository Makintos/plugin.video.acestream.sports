# -*- coding: utf-8 -*-
import sys
import xbmcaddon

from urlparse import parse_qsl

from lib import tools
from lib.kodi import Kodi
from lib.arenavision import Arenavision


__addon__ = xbmcaddon.Addon()
__version__ = __addon__.getAddonInfo('version')
__path__ = __addon__.getAddonInfo('path')
__lang__ = __addon__.getLocalizedString


# Plugin url (plugin://)
_url = sys.argv[0]

# Plugin handle
_handle = int(sys.argv[1])


_web_pages = [
    {
        'name': 'Arenavision',
        'icon': tools.build_path(__path__, 'arenavision.jpg'),
        'fanart': tools.build_path(__path__, 'arenavision_art.jpg')
    }
]


def controller(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Kodi: funciones para mostar las listas y los vídeos
    kodi = Kodi(_url, _handle)

    # Convierte la cadena de parámetros URL a un diccionario {<parameter>: <value>}
    params = dict(parse_qsl(paramstring))

    # Kodi ha invocado al script sin parámetros: muestra la lista de webs
    if not params:
        kodi.show_menu(_web_pages)

    # Hay parámetros: muestra el menú o la lista de enlaces/canales correspondiente
    else:

        # Crea los objetos y lanza el menu de la web (en params['page'])
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

        elif params['action'] == 'play':
            kodi.play_acestream_link(params['url'], params['name'], params['icon'])


if __name__ == '__main__':
    # Llama al router y le pasa la cadena de parámetros
    # Slicing para eliminar la '?' de los parámetros
    controller(sys.argv[2][1:])
