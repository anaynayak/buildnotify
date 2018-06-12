import base64
import platform
import socket
import ssl
import urllib.request, urllib.error, urllib.parse


class HttpConnection(object):
    def __init__(self):
        self.user_agent = "%s-%s" % ("BuildNotify", platform.platform())

    def connect(self, server, timeout):
        socket.setdefaulttimeout(timeout)
        headers = {'User-Agent': self.user_agent}
        if server.has_creds():
            unquoted_username = urllib.parse.unquote(server.username)
            unquoted_password = urllib.parse.unquote(server.password)
            encodedstring = base64.encodestring("%s:%s" % (unquoted_username, unquoted_password))[:-1]
            headers["Authorization"] = "Basic %s" % encodedstring
        request = urllib.request.Request(server.url, None, headers)
        if server.skip_ssl_verification:
            context = ssl._create_unverified_context()
            return urllib.request.urlopen(request, context=context)
        return urllib.request.urlopen(request)
