import re
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from buildnotifylib.core.github import GitHubError, GitHubSource, RateLimits
from buildnotifylib.core.model import Activity, Status
from buildnotifylib.core.ports import FetchError, Response
from buildnotifylib.core.projects import ProjectLoader
from buildnotifylib.core.settings import ServerSettings, SourceKind

FIXTURES = Path(__file__).parent.parent / "fixtures" / "github"
REPO = "octo-org/hello-world"
API = f"https://api.github.com/repos/{REPO}/actions/runs"
NOW = datetime(2026, 10, 2, 10, 0, tzinfo=UTC)
RESET = int((NOW + timedelta(minutes=20)).timestamp())


class FakeApi:
    def __init__(self, *responses: Response):
        self.responses = list(responses)
        self.requests: list[tuple[str, dict[str, str], bool]] = []

    def connect(self, server, timeout, additional_headers=None):
        raise AssertionError("GitHub servers are fetched with request()")

    def request(self, url, timeout, headers, verify=True):
        self.requests.append((url, headers, verify))
        return self.responses.pop(0)


def fixture(name: str, status: int = 200, **headers: str) -> Response:
    return Response(status, {k.replace("_", "-"): v for k, v in headers.items()}, (FIXTURES / name).read_bytes())


def github(**fields) -> ServerSettings:
    fields.setdefault("password", "ghp_token")
    return ServerSettings(
        "", kind=SourceKind.GITHUB, repository=REPO, authentication_type=ServerSettings.AUTH_BEARER_TOKEN, **fields
    )


def source(api, server=None, limits=None, **kwargs) -> GitHubSource:
    return GitHubSource(server or github(), 10, api, limits or RateLimits(clock=lambda: NOW), **kwargs)


def rows(projects):
    return [(p.name, p.status, p.activity, p.last_build_label) for p in projects]


def test_should_take_the_latest_run_per_workflow_and_branch():
    projects = source(FakeApi(fixture("runs.json"))).fetch()

    assert rows(projects) == [
        ("CI (main)", Status.FAILURE, Activity.BUILDING, "561"),
        ("Nightly (main)", Status.UNKNOWN, Activity.BUILDING, None),
        ("CI (feature/login)", Status.SUCCESS, Activity.SLEEPING, "560"),
        ("Release (main)", Status.UNKNOWN, Activity.SLEEPING, "41"),
        ("Lint (main)", Status.FAILURE, Activity.SLEEPING, "88"),
        ("Deploy (main)", Status.FAILURE, Activity.SLEEPING, "7"),
        ("Docs (main)", Status.UNKNOWN, Activity.SLEEPING, "3"),
    ]


def test_should_link_each_project_to_its_latest_run_and_date_its_last_finished_run():
    ci = source(FakeApi(fixture("runs.json"))).fetch()[0]

    assert ci.url == f"https://github.com/{REPO}/actions/runs/30433647"
    assert ci.server_url == f"https://github.com/{REPO}"
    assert ci.last_build_time == "2026-10-02T09:12:00Z"
    assert ci.build_time == datetime(2026, 10, 2, 9, 12, tzinfo=UTC)


def test_should_call_the_runs_api_with_a_bearer_token():
    api = FakeApi(fixture("runs.json"))
    source(api).fetch()

    url, headers, verify = api.requests[0]
    assert url == f"{API}?per_page=100"
    assert headers["Authorization"] == "Bearer ghp_token"
    assert headers["Accept"] == "application/vnd.github+json"
    assert verify is True


def test_should_call_the_api_without_a_token_for_public_repositories():
    api = FakeApi(fixture("runs.json"))
    source(api, github(password="")).fetch()

    assert "Authorization" not in api.requests[0][1]


def test_should_filter_by_branch_in_the_query_and_by_workflow_file_or_name():
    api = FakeApi(fixture("runs.json"), fixture("runs.json"))

    by_file = source(api, github(workflow="ci.yml", branch="feature/login")).fetch()
    by_name = source(api, github(workflow="Lint")).fetch()

    assert api.requests[0][0] == f"{API}?per_page=100&branch=feature%2Flogin"
    assert [p.name for p in by_file] == ["CI (main)", "CI (feature/login)"]
    assert [p.name for p in by_name] == ["Lint (main)"]


def test_should_drop_excluded_projects_unless_asked_not_to():
    server = github(excluded_projects=["Docs (main)"], prefix="gh")

    kept = source(FakeApi(fixture("runs.json")), server).fetch()
    everything = source(FakeApi(fixture("runs.json")), server, apply_excludes=False).fetch()

    assert "Docs (main)" not in [p.name for p in kept]
    assert len(everything) == 7
    assert kept[0].label() == "[gh] CI (main)"


@pytest.mark.parametrize(
    "name, status, message",
    [
        ("bad-credentials.json", 401, "GitHub rejected the token (HTTP 401)"),
        ("forbidden.json", 403, "The token can't read this repository (HTTP 403)"),
        ("not-found.json", 404, "Repository not found, or the token can't see it (HTTP 404)"),
        ("not-found.json", 500, "GitHub returned HTTP 500"),
    ],
)
def test_should_report_http_errors_in_one_short_line(name, status, message):
    with pytest.raises(FetchError, match=f"^{re.escape(message)}$"):
        source(FakeApi(fixture(name, status))).fetch()


def test_should_report_a_body_that_is_not_a_runs_list():
    with pytest.raises(GitHubError):
        source(FakeApi(Response(200, {}, b"<html>login</html>"))).fetch()
    with pytest.raises(GitHubError):
        source(FakeApi(Response(200, {}, b'{"message": "hi"}'))).fetch()


def test_should_wait_for_the_rate_limit_reset_before_calling_again():
    limited = fixture("rate-limited.json", 403, x_ratelimit_remaining="0", x_ratelimit_reset=str(RESET))
    api, limits = FakeApi(limited), RateLimits(clock=lambda: NOW)

    with pytest.raises(FetchError, match="^GitHub rate limit reached, retrying after "):
        source(api, limits=limits).fetch()
    with pytest.raises(FetchError, match="rate limit"):
        source(api, limits=limits).fetch()

    assert len(api.requests) == 1


def test_should_stop_before_the_limit_is_exceeded():
    exhausted = fixture("runs.json", x_ratelimit_remaining="0", x_ratelimit_reset=str(RESET))
    api, limits = FakeApi(exhausted), RateLimits(clock=lambda: NOW)

    assert len(source(api, limits=limits).fetch()) == 7
    with pytest.raises(FetchError, match="rate limit"):
        source(api, limits=limits).fetch()


def test_should_honour_retry_after_on_a_secondary_rate_limit():
    now = [NOW]
    limits = RateLimits(clock=lambda: now[0])
    api = FakeApi(fixture("rate-limited.json", 429, retry_after="60"), fixture("runs.json"))

    with pytest.raises(FetchError, match="rate limit"):
        source(api, limits=limits).fetch()
    now[0] = NOW + timedelta(seconds=61)

    assert len(source(api, limits=limits).fetch()) == 7


def test_should_load_github_servers_through_the_github_source():
    snapshot = ProjectLoader(github(), 10, FakeApi(fixture("bad-credentials.json", 401))).get_data()

    assert snapshot.url == f"https://github.com/{REPO}"
    assert str(snapshot.error) == "GitHub rejected the token (HTTP 401)"


@pytest.mark.parametrize(
    "response",
    [
        fixture("rate-limited.json", 429),
        Response(403, {}, b'{"message": "You have exceeded a secondary rate limit."}'),
    ],
)
def test_should_back_off_a_minute_on_a_rate_limit_without_headers(response):
    now = [NOW]
    limits = RateLimits(clock=lambda: now[0])
    api = FakeApi(response, fixture("runs.json"))

    with pytest.raises(FetchError, match="rate limit"):
        source(api, limits=limits).fetch()
    now[0] = NOW + timedelta(seconds=30)
    with pytest.raises(FetchError, match="rate limit"):
        source(api, limits=limits).fetch()
    now[0] = NOW + timedelta(seconds=61)

    assert len(source(api, limits=limits).fetch()) == 7
