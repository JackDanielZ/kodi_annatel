import urllib2
from urllib import urlencode


class Utils:
    def __init__(self):
        pass

    @staticmethod
    def get_url(url, **kwargs):
        return '{0}?{1}'.format(url, urlencode(kwargs))

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
            xbmcgui.Dialog().ok('tric', url_response.code)
            pass
        finally:
            if url_response is not None:
                url_response.close()

        return response
