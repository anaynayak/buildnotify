import requests_mock

from buildnotifylib.core.http_connection import HttpConnection
from buildnotifylib.serverconfig import ServerConfig


def test_should_pass_auth_if_provided():
    with requests_mock.Mocker() as m:
        m.get('http://localhost:8080/cc.xml', text='content')
        response = HttpConnection().connect(ServerConfig('http://localhost:8080/cc.xml', [], '', '', 'user', 'pass'), 3)
        assert str(response) == 'content'
        assert m.last_request.headers.get("Authorization")


def test_should_fetch_data_without_auth():
    with requests_mock.Mocker() as m:
        m.get('http://localhost:8080/cc.xml', text='content')
        response = HttpConnection().connect(ServerConfig('localhost:8080/cc.xml', [], '', '', None, None), 3)
        assert str(response) == 'content'
        assert not m.last_request.headers.get("Authorization")
