import os
import urllib.request

from buildnotifylib.core.http_connection import HttpConnection
from buildnotifylib.serverconfig import ServerConfig


def test_should_fetch_data():
    file_path = os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + "../../data/cctray.xml")
    response = HttpConnection().connect(ServerConfig('file://' + file_path, [], '', '', None, None), 3)
    assert str(response.read()) == open(file_path, 'r').read()


def test_should_pass_auth_if_provided(mocker):
    m = mocker.patch.object(urllib.request, 'urlopen', return_value='content')
    response = HttpConnection().connect(ServerConfig('http://localhost:8080/cc.xml', [], '', '', 'user', 'pass'), 3)
    assert str(response) == 'content'

    def url_with_auth(a):
        assert a.get_full_url() == 'http://localhost:8080/cc.xml' and a.get_header('Authorization') is not None
        return True

    m.assert_called_once_with(Matcher(url_with_auth))


def test_should_fetch_data_without_auth(mocker):
    m = mocker.patch.object(urllib.request, 'urlopen', return_value='content')
    response = HttpConnection().connect(ServerConfig('localhost:8080/cc.xml', [], '', '', None, None), 3)
    assert str(response) == 'content'

    def request_matcher(a):
        assert a.get_full_url() == 'http://localhost:8080/cc.xml' and a.get_header('Authorization') is None
        return True

    m.assert_called_once_with(Matcher(request_matcher))


class Matcher(object):
    def __init__(self, compare):
        self.compare = compare

    def __eq__(self, other):
        return self.compare(other)
