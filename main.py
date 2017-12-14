# -*- coding: utf-8 -*-
# Module: default
# Author: Roman V. M.
# Created on: 28.11.2014
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import sys
import urllib2
import io
from urllib import urlencode
from urlparse import parse_qsl
import xbmc
import xbmcgui
import xbmcplugin
import xml.etree.ElementTree as ET


def DownloadBinary(url):
    response = None
    urlResponse = None
    try:
        urlResponse = urllib2.urlopen(url)
        if (urlResponse.code == 200): # 200 = OK
            response = urlResponse.read()
    except:
        xbmcgui.Dialog().ok('tric', urlResponse.code)
        pass
    finally:
        if (urlResponse is not None):
            urlResponse.close()
    return response

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :type kwargs: dict
    :return: plugin call URL
    :rtype: str
    """
    return '{0}?{1}'.format(_url, urlencode(kwargs))

def _channel_select(url):
    m3u8_data = io.StringIO(unicode(DownloadBinary(url)))
    last_line = None

    for i in m3u8_data.readlines():
        last_line = i

    uri = url.rsplit('/', 1)[0] + '/' + last_line.strip()
    play_item = xbmcgui.ListItem()

    xbmc.Player().play(uri, play_item, False)

def list_channels():
    """
    Create the list of video categories in the Kodi interface.
    """
    print('Listing channels')
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, 'Annatel')
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')

    xml_data = DownloadBinary('http://www.annatel.tv/api/getchannels?login='+xbmcplugin.getSetting(_handle, "username")+'&password='+xbmcplugin.getSetting(_handle, "password"))
    parsed_xml = ET.fromstring(xml_data)

    for channel in parsed_xml.findall('channel'):
        name = channel.find("name").text
        logo = channel.find("logo").text
        url = channel.find("url").text.strip()

        try:
            program_title = channel.find("program_title").text
        except AttributeError:
            program_title = ''

        list_item = xbmcgui.ListItem(label=name, thumbnailImage=logo)
        list_item.setInfo('Video', {
            'title': program_title
        })
        list_item.setProperty('IsPlayable', 'true')
        call = get_url(action='channel_select', url=url)

        xbmcplugin.addDirectoryItem(_handle, call, list_item, False)

    xbmc.executebuiltin('Container.SetViewMode(%d)' % 500)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    if params:
        if params['action'] == 'channel_select':
            _channel_select(params['url'])
        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_channels()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
