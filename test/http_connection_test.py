import os
import urllib2

from buildnotifylib.core.http_connection import HttpConnection
from buildnotifylib.serverconfig import ServerConfig


def test_should_fetch_data():
    file_path = os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + "../../data/cctray.xml")
    response = HttpConnection().connect(ServerConfig('file://' + file_path, [], '', '', None, None), 10)
    assert str(response.read()) == open(file_path, 'r').read()


def test_should_pass_auth_if_provided(mocker):
    m = mocker.patch.object(urllib2, 'urlopen', return_value='content')
    response = HttpConnection().connect(ServerConfig('url', [], '', '', "user", "pass"), 10)
    assert str(response) == 'content'

    def url_with_auth(a):
        return a.get_full_url() == 'url' and a.get_header('Authorization') is not None

    m.assert_called_once_with(Matcher(url_with_auth))


class Matcher(object):
    def __init__(self, compare):
        self.compare = compare

    def __eq__(self, other):
        return self.compare(other)
