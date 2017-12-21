# -*- coding: utf-8 -*-
# Module: default
# Created on: 28.11.2017
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
        self._plugin_id = 'plugin.video.annatel'
        self._media_url = 'special://home/addons/{0}/resources/'.format(self._plugin_id)
        self._channels_uri = 'http://www.annatel.tv/api/getchannels'
        self._vod_uri = 'http://www.annatel.tv/api/xbmc/vod/date'
        self._vod_thumb = self._media_url + 'vod.jpg'
        self._cal_thumb = self._media_url + 'calendar.png'
        self._channels_map = {}
        self._channels_list = []

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
        xbmcplugin.setContent(self._handle, 'movies')

        listing = self.create_listing(list_type='live')
        xbmcplugin.addDirectoryItems(self._handle, listing, len(listing))

        list_item, call = self.create_item(label='VOD', thumbnail_image=self._vod_thumb, action='vod')
        xbmcplugin.addDirectoryItem(self._handle, call, list_item, True)
        xbmcplugin.endOfDirectory(self._handle)

    def vod(self):
        xbmcplugin.setPluginCategory(self._handle, 'Annatel')
        xbmcplugin.setContent(self._handle, 'movies')

        listing = self.create_listing(list_type='vod')
        xbmcplugin.addDirectoryItems(self._handle, listing, len(listing))
        xbmcplugin.endOfDirectory(self._handle)

    def vod_channel(self, channel):
        xbmcplugin.setPluginCategory(self._handle, 'Annatel')
        xbmcplugin.setContent(self._handle, 'files')

        try:
            uri = Utils.build_uri(self._handle, self._vod_uri,
                                  act="channel", channel=channel)
            xml_data = Utils.download_binary(uri)
        except StandardError as e:
            xbmcgui.Dialog().ok('tric', e)
            return

        listing = []
        parsed_xml = ET.fromstring(xml_data)
        for date in parsed_xml.findall("date"):
            d = date.find("day").text.encode('utf-8').strip()
            human_date = date.find("display").text.encode('utf-8').strip()

            list_item = xbmcgui.ListItem(label=human_date)
            list_item.setArt({'thumb': self._cal_thumb})
            call = Utils.get_url(action="vod_channel_day", url=self._url, channel=channel, day=d)

            listing.append((call, list_item, True))

        xbmcplugin.addDirectoryItems(self._handle, listing, len(listing))
        xbmcplugin.endOfDirectory(self._handle)

    def vod_channel_day(self, channel_id, day):
        xbmcplugin.setPluginCategory(self._handle, 'Annatel')
        xbmcplugin.setContent(self._handle, 'episodes')

        try:
            uri = Utils.build_uri(self._handle, self._vod_uri,
                                  act="program", channel=channel_id, day=day)
            xml_data = Utils.download_binary(uri)
        except StandardError as e:
            xbmcgui.Dialog().ok('tric', e)
            return

        listing = []
        parsed_xml = ET.fromstring(xml_data)
        for program in parsed_xml.findall('program'):
            try:
                name = program.find("name").text.encode('utf-8').strip()
            except AttributeError:
                name = ''

            try:
                description = program.find("description").text.encode('utf-8').strip()
            except AttributeError:
                description = ''

            try:
                url = program.find("url").text.encode('utf-8').strip()
            except AttributeError:
                url = None

            if url is not None:
                logo = self.retrieve_channel_logo(channel_id)
                list_item = xbmcgui.ListItem(label=name)
                list_item.setProperty('IsPlayable', 'true')
                list_item.setArt({'thumb': logo})
                list_item.setInfo('video', {
                    'title': name,
                    'episodeguide': description
                })
                call = Utils.get_url(action='channel_select', url=url)
                listing.append((call, list_item, False))

        xbmcplugin.addDirectoryItems(self._handle, listing, len(listing))
        xbmcplugin.endOfDirectory(self._handle)

    def retrieve_channel_logo(self, channel_id):
        try:
            uri = Utils.build_uri(self._handle, self._vod_uri)
            xml_data = Utils.download_binary(uri)
        except StandardError as e:
            xbmcgui.Dialog().ok('tric', e)
            return

        parsed_xml = ET.fromstring(xml_data)

        for channel in parsed_xml.findall('channel'):
            cid = channel.find('stream').text.encode('utf-8').strip()
            name = channel.find('name').text.encode('utf-8').strip()

            if cid == channel_id:
                if name in self._channels_map:
                    return self._channels_map[name]['logo']

                return None

    def map_channels(self):
        i = 0
        try:
            xml_data = Utils.download_binary(Utils.build_uri(self._handle, self._channels_uri))
        except StandardError as e:
            xbmcgui.Dialog().ok('tric', e)
            return

        try:
            vod_xml_data = Utils.download_binary(Utils.build_uri(self._handle, self._vod_uri))
        except StandardError as e:
            xbmcgui.Dialog().ok('tric', e)
            return

        parsed_xml = ET.fromstring(xml_data)
        vod_parsed_xml = ET.fromstring(vod_xml_data)

        for channel in parsed_xml.findall('channel'):
            try:
                name = channel.find("name").text.encode('utf-8').strip()
            except AttributeError:
                name = None

            try:
                logo = channel.find("logo").text.encode('utf-8')
            except AttributeError:
                logo = ''

            try:
                url = channel.find("url").text.encode('utf-8').strip()
            except AttributeError:
                url = None

            try:
                program_title = channel.find("program_title").text.encode('utf-8').strip()
            except AttributeError:
                program_title = ''

            if name is not None:
                self._channels_list.append(name)
                self._channels_map[name] = {
                    "name": name,
                    "logo": logo,
                    "url": url,
                    "program_title": program_title
                }

                for vod_channel in vod_parsed_xml.findall('channel'):
                    try:
                        vod_name = vod_channel.find("name").text.encode('utf-8').strip()
                    except AttributeError:
                        continue

                    if vod_name == name:
                        self._channels_map[name]['id'] = vod_channel.find('stream').text.encode('utf-8').strip()

    def create_listing(self, list_type):
        listing = []
        is_live = list_type != 'vod'
        is_folder = False if is_live else True
        action = 'channel_select' if is_live else 'vod_channel'

        for channel in self._channels_list:
            call = None

            if channel in self._channels_map:
                value = self._channels_map[channel]

                if value['url'] is not None:
                    name = value['name']
                    logo = value['logo']
                    url = value['url'] if is_live else self._url
                    program_title = value['program_title']

                    list_item = xbmcgui.ListItem(label=name)
                    list_item.setArt({'thumb': logo})

                    if is_live:
                        list_item.setProperty('IsPlayable', 'true')
                        list_item.setInfo('video', {
                            'title': program_title
                        })
                        call = Utils.get_url(action=action, url=url)
                    else:
                        if 'id' in value:
                            channel_id = value['id']
                            call = Utils.get_url(action=action, url=url, channel=channel_id)

                    if call is not None:
                        listing.append((call, list_item, is_folder))

        return listing

    def create_item(self, label, thumbnail_image, action, url=None):
        list_item = xbmcgui.ListItem(label=label)
        list_item.setArt({'thumb': thumbnail_image})
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
        print params
        if params['action'] == 'channel_select':
            annatel.channel_select(params['url'])
        elif params['action'] == 'vod':
            annatel.vod()
        elif params['action'] == 'vod_channel':
            annatel.vod_channel(params['channel'])
        elif params['action'] == 'vod_channel_day':
            annatel.vod_channel_day(params['channel'], params['day'])
        else:
            raise ValueError('Invalid param_string: {0}!'.format(param_string))
    else:
        annatel.list_channels()


if __name__ == '__main__':
    router(sys.argv[2][1:])
