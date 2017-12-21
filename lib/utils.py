import urllib2
import xbmcplugin
from urllib import urlencode


class Utils:
    def __init__(self):
        pass

    @staticmethod
    def get_url(url, **kwargs):
        op = '?' if '?' not in url else '&'
        return '{0}{1}{2}'.format(url, op, urlencode(kwargs))

    @staticmethod
    def download_binary(url):
        response = None
        url_response = None
        try:
            url_response = urllib2.urlopen(url)
            if url_response.code == 200:
                response = url_response.read()
        except urllib2.URLError:
            raise StandardError(url_response.code)
            pass
        finally:
            if url_response is not None:
                url_response.close()

        return response

    @staticmethod
    def build_uri(handle, url, **kwargs):
        return "{0}?login={1}&password={2}&{3}".format(url,
                                                       xbmcplugin.getSetting(handle, "username"),
                                                       xbmcplugin.getSetting(handle, "password"),
                                                       urlencode(kwargs))
