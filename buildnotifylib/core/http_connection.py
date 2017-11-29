import base64
import platform
import socket
import ssl
import urllib2
from urlparse import urlparse


class HttpConnection(object):
    def __init__(self):
        self.user_agent = "%s-%s" % ("BuildNotify", platform.platform())

    def connect(self, server, timeout):
        socket.setdefaulttimeout(timeout)
        headers = {'User-Agent': self.user_agent}
        if server.has_creds():
            unquoted_username = urllib2.unquote(server.username)
            unquoted_password = urllib2.unquote(server.password)
            encodedstring = base64.encodestring("%s:%s" % (unquoted_username, unquoted_password))[:-1]
            headers["Authorization"] = "Basic %s" % encodedstring
        parsed = urlparse(server.url)
        url = parsed.geturl() if parsed.scheme else 'http://' + server.url
        if server.skip_ssl_verification:
            return urllib2.urlopen(urllib2.Request(url, None, headers), context=ssl._create_unverified_context())
        return urllib2.urlopen(urllib2.Request(url, None, headers))
