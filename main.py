# -*- coding: utf-8 -*-
# Module: default
# Author: Roman V. M.
# Created on: 28.11.2014
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import sys
import io
from urlparse import parse_qsl
from lib.utils import Utils
import xbmc
import xbmcgui
import xbmcplugin
import xml.etree.ElementTree as ET


class Annatel:
    def __init__(self):
        self._url = sys.argv[0]
        self._handle = int(sys.argv[1])
        self._channels_uri = 'http://www.annatel.tv/api/getchannels'
        self._vod_uri = 'http://www.annatel.tv/api/xbmc/vod/date'
        self._vod_thumb = 'http://bestmediainfo.com/wp-content/uploads/2016/03/video-on-demand.jpg'
        self.channels_map = {}

        self.map_channels()

    def channel_select(self, url):
        m3u8_data = io.StringIO(unicode(Utils.download_binary(url)))
        last_line = None

        for i in m3u8_data.readlines():
            last_line = i

        uri = url.rsplit('/', 1)[0] + '/' + last_line.strip()
        play_item = xbmcgui.ListItem()

        xbmc.Player().play(uri, play_item, False)

    def list_channels(self):
        xbmcplugin.setPluginCategory(self._handle, 'Annatel')
        xbmcplugin.setContent(self._handle, 'videos')

        listing = self.create_listing(xml=None)
        xbmcplugin.addDirectoryItems(self._handle, listing, len(listing))

        list_item, call = self.create_item(label='VOD', thumbnail_image=self._vod_thumb, action='vod')
        xbmcplugin.addDirectoryItem(self._handle, call, list_item, True)

        xbmc.executebuiltin('Container.SetViewMode(%d)' % 500)
        xbmcplugin.endOfDirectory(self._handle)

    def vod(self):
        try:
            xml_data = Utils.download_binary(self._vod_uri + '?login=' +
                                             xbmcplugin.getSetting(self._handle, "username") + '&password=' +
                                             xbmcplugin.getSetting(self._handle, "password"))
        except StandardError as e:
            xbmcgui.Dialog().ok('tric', e)
            return

        parsed_xml = ET.fromstring(xml_data)

        listing = self.create_listing(parsed_xml)
        xbmcplugin.addDirectoryItems(self._handle, listing, len(listing))

        xbmc.executebuiltin('Container.SetViewMode(%d)' % 500)
        xbmcplugin.endOfDirectory(self._handle)

    def map_channels(self):
        try:
            xml_data = Utils.download_binary(self._channels_uri + '?login=' +
                                             xbmcplugin.getSetting(self._handle, "username") + '&password=' +
                                             xbmcplugin.getSetting(self._handle, "password"))
        except StandardError as e:
            xbmcgui.Dialog().ok('tric', e)
            return

        parsed_xml = ET.fromstring(xml_data)

        for channel in parsed_xml.findall('channel'):
            try:
                name = channel.find("name").text
            except AttributeError:
                name = ''

            try:
                logo = channel.find("logo").text
            except AttributeError:
                logo = ''

            try:
                url = channel.find("url").text.strip()
            except AttributeError:
                url = None

            try:
                program_title = channel.find("program_title").text
            except AttributeError:
                program_title = ''

            self.channels_map[name] = {
                "name": name,
                "logo": logo,
                "url": url,
                "program_title": program_title
            }

    def create_listing(self, xml):
        listing = []
        mapping = {}
        is_folder = True if xml is None else False
        action = 'vod_select' if xml is None else 'channel_select'

        if xml is None:
            mapping = self.channels_map
        else:
            for channel in xml.findall('channel'):
                try:
                    name = channel.find("name").text
                except AttributeError:
                    continue

                if name in self.channels_map:
                    mapping[name] = self.channels_map[name]

        for channel, value in mapping.iteritems():
            if value.url is not None:
                name = value.name
                logo = value.logo
                url = self._url if xml is None else value.url
                program_title = value.program_title

                list_item = xbmcgui.ListItem(label=name, thumbnailImage=logo)

                if xml is not None:
                    list_item.setProperty('IsPlayable', 'true')
                    list_item.setInfo('Video', {
                        'title': program_title
                    })

                call = Utils.get_url(action=action, url=url)
                listing.append((call, list_item, is_folder))

        return listing

    def create_item(self, label, thumbnail_image, action, url):
        list_item = xbmcgui.ListItem(label=label, thumbnailImage=thumbnail_image)
        list_item.setInfo('Video', {
            'title': label
        })
        call = Utils.get_url(action=action, url=url if url is not None else self._url)

        return list_item, call


def router(param_string):
    """
    Router function that calls other functions
    depending on the provided param_string

    :param param_string: URL encoded plugin paramstring
    :type param_string: str
    """
    # Parse a URL-encoded param_string to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(param_string))
    annatel = Annatel()

    if params:
        if params['action'] == 'channel_select':
            annatel.channel_select(params['url'])
        elif params['action'] == 'vod':
            annatel.vod()
        else:
            raise ValueError('Invalid param_string: {0}!'.format(param_string))
    else:
        annatel.list_channels()


if __name__ == '__main__':
    router(sys.argv[2][1:])
