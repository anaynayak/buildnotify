import base64
import ssl
import threading

import pytest
import requests
import requests_mock

from buildnotifylib.adapters.http import HttpConnection
from buildnotifylib.core.ports import CertificateError
from buildnotifylib.core.projects import ProjectLoader
from buildnotifylib.core.settings import ServerSettings
from buildnotifylib.version import VERSION


def test_should_pass_auth_if_provided():
    with requests_mock.Mocker() as m:
        m.get("http://localhost:8080/cc.xml", text="content")
        server = ServerSettings("http://localhost:8080/cc.xml", username="user", password="pass")
        response = HttpConnection().connect(server, 3)
        assert response == b"content"
        assert m.last_request.headers.get("Authorization")


def test_should_fetch_data_without_auth():
    with requests_mock.Mocker() as m:
        m.get("http://localhost:8080/cc.xml", text="content")
        response = HttpConnection().connect(ServerSettings("localhost:8080/cc.xml", [], "", "", None, None), 3)
        assert response == b"content"
        assert not m.last_request.headers.get("Authorization")


def test_should_send_user_agent_without_platform_details():
    with requests_mock.Mocker() as m:
        m.get("http://localhost:8080/cc.xml", text="content")
        HttpConnection().connect(ServerSettings("localhost:8080/cc.xml", [], "", "", None, None), 3)
        assert m.last_request.headers["User-Agent"] == f"BuildNotify/{VERSION}"


def bearer_config(username):
    return ServerSettings(
        "http://localhost:8080/cc.xml",
        [],
        "",
        "",
        username,
        "token",
        authentication_type=ServerSettings.AUTH_BEARER_TOKEN,
    )


@pytest.mark.parametrize("username", [None, "", "leftover-user"])
def test_should_send_only_bearer_token_for_bearer_auth(username):
    with requests_mock.Mocker() as m:
        m.get("http://localhost:8080/cc.xml", text="<Projects/>")
        response = ProjectLoader(bearer_config(username), 3, HttpConnection()).get_data()
        assert not response.unavailable
        assert m.last_request.headers["Authorization"] == "Bearer token"


def test_should_send_basic_auth_for_username_password():
    with requests_mock.Mocker() as m:
        m.get("http://localhost:8080/cc.xml", text="<Projects/>")
        ProjectLoader(
            ServerSettings("http://localhost:8080/cc.xml", [], "", "", "user", "pass"), 3, HttpConnection()
        ).get_data()
        expected = "Basic " + base64.b64encode(b"user:pass").decode()
        assert m.last_request.headers["Authorization"] == expected


def test_should_report_ssl_error():
    with requests_mock.Mocker() as m:
        m.get("https://localhost:8080/cc.xml", exc=requests.exceptions.SSLError("bad certificate"))
        config = ServerSettings("https://localhost:8080/cc.xml", [], "", "", None, None)
        response = ProjectLoader(config, 3, HttpConnection()).get_data()
        assert isinstance(response.error, CertificateError)
        assert str(response.error) == "bad certificate"
        assert response.unavailable


def test_should_reuse_one_session_per_thread_across_polls(mocker):
    connection = HttpConnection()
    new_session = mocker.spy(requests.sessions.Session, "__init__")
    with requests_mock.Mocker() as m:
        m.get("http://localhost:8080/cc.xml", text="content")
        config = ServerSettings("localhost:8080/cc.xml", [], "", "", None, None)
        connection.connect(config, 3)
        connection.connect(config, 3)
        assert m.call_count == 2
    assert new_session.call_count == 1


def test_should_not_share_a_session_between_fetch_threads():
    connection = HttpConnection()
    sessions = [connection.session]
    worker = threading.Thread(target=lambda: sessions.append(connection.session))
    worker.start()
    worker.join(5)

    assert len(sessions) == 2 and sessions[0] is not sessions[1]
    assert connection.session is sessions[0]


def test_should_honour_encoding_declared_in_the_feed():
    body = (
        '<?xml version="1.0" encoding="ISO-8859-1"?>'
        '<Projects><Project name="café" activity="Sleeping" lastBuildStatus="Success"/></Projects>'
    )
    with requests_mock.Mocker() as m:
        m.get("http://localhost:8080/cc.xml", content=body.encode("iso-8859-1"))
        config = ServerSettings("localhost:8080/cc.xml", [], "", "", None, None)
        response = ProjectLoader(config, 3, HttpConnection()).get_data()
        assert [p.name for p in response.projects] == ["café"]


def load_failing_with(error: Exception) -> Exception | None:
    with requests_mock.Mocker() as m:
        m.get("https://localhost:8080/cc.xml", exc=error)
        config = ServerSettings("https://localhost:8080/cc.xml")
        return ProjectLoader(config, 3, HttpConnection()).get_data().error


def test_should_recognise_ssl_error_subclasses():
    class BadCertificate(requests.exceptions.SSLError):
        pass

    assert isinstance(load_failing_with(BadCertificate()), CertificateError)


@pytest.mark.parametrize("error", [ValueError(), ssl.SSLError(), requests.exceptions.ConnectionError()])
def test_should_not_treat_other_errors_as_ssl_errors(error):
    assert not isinstance(load_failing_with(error), CertificateError)
