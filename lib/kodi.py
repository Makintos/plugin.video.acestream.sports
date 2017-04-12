# -*- coding: utf-8 -*-
import urllib

import xbmc
import xbmcgui
import xbmcplugin

from urllib import urlencode
from lib import tools


class Kodi:

    def __init__(self, plugin_url, plugin_handle):
        self.__url = plugin_url
        self.__handle = plugin_handle

    def __get_url(self, **kwargs):
        """
        Create a URL for calling the plugin recursively from the given set of keyword arguments.

        :param kwargs: "argument=value" pairs
        :type kwargs: str
        :return: plugin call URL
        :rtype: str
        """
        return '{0}?{1}'.format(self.__url, urlencode(kwargs, 'utf-8'))

    def show_menu(self, entries, source=None, sort_method=xbmcplugin.SORT_METHOD_NONE, show_plot=False):
        """
        Create the list of menu entries in the Kodi interface.
        """
        # Iterate through categories
        for entry in entries:
            # Create a list item with a text label and a thumbnail image
            list_item = xbmcgui.ListItem(label=entry['name'])

            # Set additional info for the list item
            # Description, year, duration, plot...

            info = {
                'title': entry['name'],
                'genre': 'Sports'
            }

            if show_plot:
                info['plot'] = entry['name']

            list_item.setInfo('video', info)

            # Set graphics for the list item
            # Thumbnail, fanart, banner, poster, landscape...

            art = {
                'thumb': entry['icon'],
                'poster': entry['icon']
            }

            if 'fanart' in entry:
                art['fanart'] = entry['fanart']

            list_item.setArt(art)

            # Create a URL for a plugin recursive call
            # plugin://plugin.video.acestream.sports/?source=Arenavision&action=show&item=Hoy%20y%20mana%2Ca

            # Si no hay source vengo del menú principal y voy a la página entry['name']
            if source is None:
                url = self.__get_url(action='show', page=entry['name'])

            # Si hay channel_url vengo de la lista de eventos de LiveFootbalLOL y voy a lista de enlaces (AV8, Canal1..)
            elif 'channel_url' in entry:
                url = self.__get_url(source=source, action='show', event=entry['channel_url'])

            # Si hay competición vengo de la lista de eventos de Arenavision y voy a la lista de enlaces (AV8, Canal1..)
            elif 'competition' in entry:
                try:
                    url = self.__get_url(source=source, action='show',
                                         event=entry['name'].encode('utf-8'), date=entry['date'], time=entry['time'])
                except UnicodeDecodeError:
                    url = self.__get_url(source=source, action='show',
                                         event=entry['name'], date=entry['date'], time=entry['time'])

            # Si hay sport_id vengo de la lista de deportes y voy a la lista de enlaces (AV8, AV9...)
            elif 'sport_id' in entry:
                url = self.__get_url(source=source, action='show', sport_id=entry['sport_id'])

            # Si hay competition_id vengo de la lista de competiciones y voy a la lista de enlaces (AV8, AV9...)
            elif 'competition_id' in entry:
                url = self.__get_url(source=source, action='show', competition_id=entry['competition_id'])

            # Si hay category_id vengo de la lista de categorías de TorrentTV y voy a la lista de enlaces (canales)
            elif 'category_id' in entry:
                url = self.__get_url(source=source, action='show', category_id=entry['category_id'])

            # Vengo de entry['name'] y voy a la lista de eventos/deportes/competiciones
            else:
                url = self.__get_url(source=source, action='show', item=entry['name'])

            # is_folder = True means that this item opens a sub-list of lower level items
            is_folder = True

            # Add our item to the Kodi virtual folder listing.
            xbmcplugin.addDirectoryItem(self.__handle, url, list_item, is_folder)

        # Add a sort method for the virtual folder items (default none)
        xbmcplugin.addSortMethod(self.__handle, sort_method)

        # Finish creating a virtual folder.
        xbmcplugin.endOfDirectory(self.__handle)

    def show_events(self, events, show_plot=False):
        """
        Create the list of event links in the Kodi interface.

        :param events: The events list
        :type events: list
        :param show_plot: Show name as description
        :type show_plot: bool
        """
        # Iterate through events.
        for event in events:
            # Create a list item with a text label and a thumbnail image.
            list_item = xbmcgui.ListItem(label=event['name'])

            # Set additional info for the list item
            # Description, year, duration, plot...

            info = {
                'title': event['name'],
                'genre': 'Sports'
            }

            if show_plot:
                info['plot'] = event['name']

            list_item.setInfo('video', info)

            # Set graphics for the list item
            # Thumbnail, fanart, banner, poster, landscape...

            list_item.setArt({
                'thumb': event['icon'],
                'icon': event['icon'],
                'fanart': event['fanart']}
            )

            # Create a URL for a plugin recursive call.
            # plugin://plugin.video.acestream.sports/?source=Arenavision&action=play&url=2af45ce4cd32c3998af2ed

            url = self.__get_url(
                source='acestream',
                action='play',
                url=event['hash'],
                name=event['name'],
                icon=event['icon']
            )

            # Add the list item to a virtual Kodi folder.
            # is_folder = False means that this item won't open any sub-list.
            is_folder = False

            # Add our item to the Kodi virtual folder listing.
            xbmcplugin.addDirectoryItem(self.__handle, url, list_item, is_folder)

        # Add a sort method for the virtual folder items (alphabetically, ignore articles)
        xbmcplugin.addSortMethod(self.__handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)

        # Finish creating a virtual folder.
        xbmcplugin.endOfDirectory(self.__handle)

    def play_acestream_link(self, url, name='Video', icon=None):
        """
        Play an acestream link by the provided name, icon and url.

        :param url: Acestream url
        :type url: str
        :param name: Link name
        :type name: str
        :param icon: Icon url
        :type icon: str
        """
        _plexus_uri = 'plugin://program.plexus/?mode=1&url={CHURL}&name={CHNAME}'\
            .format(
                CHURL=urllib.quote(url, safe=''),
                CHNAME=urllib.quote(name, safe='')
            )

        if icon:
            _plexus_uri += "&iconimage={CHICON}".format(CHICON=urllib.quote(icon, safe=''))

        tools.write_log('PLAY: %s | %s' % (name, url))
        tools.write_log('URI: "{0}"'.format(_plexus_uri))

        xbmc.Player().play("{0}".format(_plexus_uri))
