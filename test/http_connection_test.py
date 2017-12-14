import os
import urllib2

from buildnotifylib.core.http_connection import HttpConnection
from buildnotifylib.serverconfig import ServerConfig


def test_should_fetch_data():
    file_path = os.path.realpath(os.path.dirname(os.path.abspath(__file__)) + "../../data/cctray.xml")
    response = HttpConnection().connect(ServerConfig('file://' + file_path, [], '', '', None, None), 3)
    assert str(response.read()) == open(file_path, 'r').read()


def test_should_pass_auth_if_provided(mocker):
    validate_for(mocker, 'http://url.com:9800/cc.xml', 'user', 'pass', 'http://url.com:9800/cc.xml')
    validate_for(mocker, 'url.com:9800/cc.xml', 'user', 'pass', 'http://url.com:9800/cc.xml')
    validate_for(mocker, 'url.com/cc.xml', 'user', 'pass', 'http://url.com/cc.xml')
    validate_for(mocker, 'localhost:8080/cc.xml', 'user', 'pass', 'http://localhost:8080/cc.xml')
    validate_for(mocker, 'http://localhost:8080/cc.xml', 'user', 'pass', 'http://localhost:8080/cc.xml')
    validate_for(mocker, 'https://localhost:8080/cc.xml', 'user', 'pass', 'https://localhost:8080/cc.xml')
    validate_for(mocker, 'file://localhost:8080/cc.xml', 'user', 'pass', 'file://localhost:8080/cc.xml')
    # validate_for(mocker, 'http://localhost:8080/cc.xml', None, None, 'http://localhost:8080/cc.xml')


def validate_for(mocker, url, user, password, expected_url):
    m = mocker.patch.object(urllib2, 'urlopen', return_value='content')
    response = HttpConnection().connect(ServerConfig(url, [], '', '', user, password), 3)
    assert str(response) == 'content'

    def url_with_auth(a):
        assert a.get_full_url() == expected_url and a.get_header('Authorization') is not None
        return True

    m.assert_called_once_with(Matcher(url_with_auth))


class Matcher(object):
    def __init__(self, compare):
        self.compare = compare

    def __eq__(self, other):
        return self.compare(other)
