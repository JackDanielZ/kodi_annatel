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

# Free sample videos are provided by www.vidsplay.com
# Here we use a fixed set of properties simply for demonstrating purposes
# In a "real life" plugin you will need to get info and links to video files/streams
# from some web-site or online service.
VIDEOS = {'ZZZAnimals': [{'name': 'Crab',
                       'thumb': 'http://www.vidsplay.com/wp-content/uploads/2017/04/crab-screenshot.jpg',
                       'video': 'special://temp/channel.strm',
                       'genre': 'Animals'},
                      {'name': 'Alligator',
                       'thumb': 'http://www.vidsplay.com/wp-content/uploads/2017/04/alligator-screenshot.jpg',
                       'video': '/media/Storage/truc.strm',
                       'genre': 'Animals'},
                      {'name': 'Turtle',
                       'thumb': 'http://www.vidsplay.com/wp-content/uploads/2017/04/turtle-screenshot.jpg',
                       'video': 'http://www.vidsplay.com/wp-content/uploads/2017/04/turtle.mp4',
                       'genre': 'Animals'}
                      ],
            'Cars': [{'name': 'Postal Truck',
                      'thumb': 'http://www.vidsplay.com/wp-content/uploads/2017/05/us_postal-screenshot.jpg',
                      'video': 'http://82.80.192.242/smooths_live/tf1.isml/tf1-audio1=96000-video=1600000-574388.ts?token=28a649-71ca6f6-1b20b40b-2234234c',
                      'genre': 'Cars'},
                     {'name': 'Traffic',
                      'thumb': 'http://www.vidsplay.com/wp-content/uploads/2017/05/traffic1-screenshot.jpg',
                      'video': 'http://www.vidsplay.com/wp-content/uploads/2017/05/traffic1.mp4',
                      'genre': 'Cars'},
                     {'name': 'Traffic Arrows',
                      'thumb': 'http://www.vidsplay.com/wp-content/uploads/2017/05/traffic_arrows-screenshot.jpg',
                      'video': 'http://www.vidsplay.com/wp-content/uploads/2017/05/traffic_arrows.mp4',
                      'genre': 'Cars'}
                     ],
            'Food': [{'name': 'Chicken',
                      'thumb': 'http://www.vidsplay.com/wp-content/uploads/2017/05/bbq_chicken-screenshot.jpg',
                      'video': 'http://www.vidsplay.com/wp-content/uploads/2017/05/bbqchicken.mp4',
                      'genre': 'Food'},
                     {'name': 'Hamburger',
                      'thumb': 'http://www.vidsplay.com/wp-content/uploads/2017/05/hamburger-screenshot.jpg',
                      'video': 'http://www.vidsplay.com/wp-content/uploads/2017/05/hamburger.mp4',
                      'genre': 'Food'},
                     {'name': 'Pizza',
                      'thumb': 'http://www.vidsplay.com/wp-content/uploads/2017/05/pizza-screenshot.jpg',
                      'video': 'http://www.vidsplay.com/wp-content/uploads/2017/05/pizza.mp4',
                      'genre': 'Food'}
                     ]}


def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :type kwargs: dict
    :return: plugin call URL
    :rtype: str
    """
    return '{0}?{1}'.format(_url, urlencode(kwargs))


def get_categories():
    """
    Get the list of video categories.

    Here you can insert some parsing code that retrieves
    the list of video categories (e.g. 'Movies', 'TV-shows', 'Documentaries' etc.)
    from some site or server.

    .. note:: Consider using `generator functions <https://wiki.python.org/moin/Generators>`_
        instead of returning lists.

    :return: The list of video categories
    :rtype: list
    """
    return VIDEOS.keys()


def get_videos(category):
    """
    Get the list of videofiles/streams.

    Here you can insert some parsing code that retrieves
    the list of video streams in the given category from some site or server.

    .. note:: Consider using `generators functions <https://wiki.python.org/moin/Generators>`_
        instead of returning lists.

    :param category: Category name
    :type category: str
    :return: the list of videos in the category
    :rtype: list
    """
    return VIDEOS[category]

"""
def _channel_ts_data_get(base, url):
    m3u8_data = io.StringIO(unicode(DownloadBinary(base + url)))
    last = None
    ts_file = open('/tmp/truc.ts', 'w');
    for i in m3u8_data.readlines():
        if i[:1] != '#':
            ts_data = DownloadBinary(base + i)
            ts_file.write(ts_data);
    ts_file.close()
    #play_item = xbmcgui.ListItem(path = '/tmp/truc.ts')
    play_item = xbmcgui.ListItem(path = '/media/Storage/truc.strm')
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(_handle, True, play_item)

21:05:46.502 T:140468238940224   DEBUG: CCurlFile::GetMimeType - http://82.80.192.242/smooths_live/tf1.isml/tf1-audio1=96000-video=1600000.m3u8?token=28a649-71ca6f6-1b20b40b-2234234c -> application/vnd.apple.mpegurl

21:02:09.659 T:140468238940224   DEBUG: CCurlFile::GetMimeType - http://82.80.192.242/smooths_live/france2.isml/france2-audio1=96000-video=1600000.m3u8?token=28a649-71ca6f6-1b20b40b-2234234c

"""


def _channel_select(url):
    m3u8_data = io.StringIO(unicode(DownloadBinary(url)))
    last_line = None

    for i in m3u8_data.readlines():
        last_line = i

    uri = url.rsplit('/', 1)[0] + '/' + last_line
    play_item = xbmcgui.ListItem()

    xbmc.Player().play(uri, play_item, False)


def list_categories():
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

    """xml_data = DownloadBinary('http://www.annatel.tv/api/getchannels?login=%s&password=%s')"""
    xml_file = open('/tmp/annatel.xml', 'r')
    xml_data = xml_file.read()
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


def list_videos(category):
    """
    Create the list of playable videos in the Kodi interface.

    :param category: Category name
    :type category: str
    """

    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, category)
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get the list of videos in the category.
    videos = get_videos(category)
    # Iterate through videos.
    for video in videos:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=video['name'])
        # Set additional info for the list item.
        list_item.setInfo('video', {'title': video['name'], 'genre': video['genre']})
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': video['thumb'], 'icon': video['thumb'], 'fanart': video['thumb']})
        # Set 'IsPlayable' property to 'true'.
        # This is mandatory for playable items!
        list_item.setProperty('IsPlayable', 'true')
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/wp-content/uploads/2017/04/crab.mp4
        url = get_url(action='play', video=video['video'])
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = False
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def play_video(path):
    """
    Play a video by the provided path.

    :param path: Fully-qualified video URL
    :type path: str
    """
    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=path)
    # Pass the item to the Kodi player.
    print("ZZZ" + path + "ZZZ")
    xbmc.Player ().play(path, play_item, False) 
#    xbmcplugin.setResolvedUrl(_handle, True, play_item)


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
        elif params['action'] == 'listing':
            # Display the list of videos in a provided category.
            list_videos(params['category'])
        elif params['action'] == 'play':
            # Play a video from a provided URL.
            play_video(params['video'])
        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_categories()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
