import base64

import pytest
import requests
import requests_mock

from buildnotifylib.core.http_connection import HttpConnection
from buildnotifylib.core.projects import ProjectLoader
from buildnotifylib.serverconfig import ServerConfig
from buildnotifylib.version import VERSION


def test_should_pass_auth_if_provided():
    with requests_mock.Mocker() as m:
        m.get("http://localhost:8080/cc.xml", text="content")
        response = HttpConnection().connect(ServerConfig("http://localhost:8080/cc.xml", [], "", "", "user", "pass"), 3)
        assert response == b"content"
        assert m.last_request.headers.get("Authorization")


def test_should_fetch_data_without_auth():
    with requests_mock.Mocker() as m:
        m.get("http://localhost:8080/cc.xml", text="content")
        response = HttpConnection().connect(ServerConfig("localhost:8080/cc.xml", [], "", "", None, None), 3)
        assert response == b"content"
        assert not m.last_request.headers.get("Authorization")


def test_should_send_user_agent_without_platform_details():
    with requests_mock.Mocker() as m:
        m.get("http://localhost:8080/cc.xml", text="content")
        HttpConnection().connect(ServerConfig("localhost:8080/cc.xml", [], "", "", None, None), 3)
        assert m.last_request.headers["User-Agent"] == "BuildNotify/%s" % VERSION


def bearer_config(username):
    return ServerConfig(
        "http://localhost:8080/cc.xml",
        [],
        "",
        "",
        username,
        "token",
        authentication_type=ServerConfig.AUTH_BEARER_TOKEN,
    )


@pytest.mark.parametrize("username", [None, "", "leftover-user"])
def test_should_send_only_bearer_token_for_bearer_auth(username):
    with requests_mock.Mocker() as m:
        m.get("http://localhost:8080/cc.xml", text="<Projects/>")
        response = ProjectLoader(bearer_config(username), 3, HttpConnection()).get_data()
        assert not response.failed()
        assert m.last_request.headers["Authorization"] == "Bearer token"


def test_should_send_basic_auth_for_username_password():
    with requests_mock.Mocker() as m:
        m.get("http://localhost:8080/cc.xml", text="<Projects/>")
        ProjectLoader(
            ServerConfig("http://localhost:8080/cc.xml", [], "", "", "user", "pass"), 3, HttpConnection()
        ).get_data()
        expected = "Basic " + base64.b64encode(b"user:pass").decode()
        assert m.last_request.headers["Authorization"] == expected


def test_should_report_ssl_error():
    with requests_mock.Mocker() as m:
        m.get("https://localhost:8080/cc.xml", exc=requests.exceptions.SSLError("bad certificate"))
        config = ServerConfig("https://localhost:8080/cc.xml", [], "", "", None, None)
        response = ProjectLoader(config, 3, HttpConnection()).get_data()
        assert response.ssl_error()
        assert response.server.unavailable


def test_should_reuse_one_session_across_polls(mocker):
    connection = HttpConnection()
    new_session = mocker.spy(requests.sessions.Session, "__init__")
    with requests_mock.Mocker() as m:
        m.get("http://localhost:8080/cc.xml", text="content")
        config = ServerConfig("localhost:8080/cc.xml", [], "", "", None, None)
        connection.connect(config, 3)
        connection.connect(config, 3)
        assert m.call_count == 2
    assert new_session.call_count == 0


def test_should_honour_encoding_declared_in_the_feed():
    body = (
        '<?xml version="1.0" encoding="ISO-8859-1"?>'
        '<Projects><Project name="café" activity="Sleeping" lastBuildStatus="Success"/></Projects>'
    )
    with requests_mock.Mocker() as m:
        m.get("http://localhost:8080/cc.xml", content=body.encode("iso-8859-1"))
        config = ServerConfig("localhost:8080/cc.xml", [], "", "", None, None)
        response = ProjectLoader(config, 3, HttpConnection()).get_data()
        assert [p.name for p in response.server.get_projects()] == ["café"]
