import socket
import urllib2
import urlparse
import base64
class HttpConnection:
    def connect(self, url, timeout):
        socket.setdefaulttimeout(timeout)
        urlparts = urlparse.urlparse(url)
        username, password = urlparts.username, urlparts.password
        replace_string = "%s:%s@" % (username, password)
        host = urlparts.netloc.replace(replace_string, "" )
        url_without_auth = urlparse.urlunparse((urlparts.scheme,host, urlparts.path, urlparts.params, urlparts.query, urlparts.fragment))
        headers = {}
        if username is not None:
            encodedstring = base64.encodestring("%s:%s" % (username, password))[:-1]
            headers["Authorization"] = "Basic %s" % encodedstring
        return urllib2.urlopen(urllib2.Request(url_without_auth, None, headers))
