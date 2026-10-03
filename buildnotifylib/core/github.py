"""GitHub Actions as a Source: the latest workflow run per workflow and branch becomes a Project."""

import hashlib
import json
import re
from collections.abc import Callable, Mapping
from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import urlencode

from buildnotifylib.core.cctray import parse_build_time
from buildnotifylib.core.model import NONE_TIMEZONE, Activity, Project, Status
from buildnotifylib.core.ports import Connection, FetchError, Response
from buildnotifylib.core.settings import ServerSettings

API = "https://api.github.com"
HEADERS = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
CONCLUSIONS = {
    "success": Status.SUCCESS,
    "failure": Status.FAILURE,
    "timed_out": Status.FAILURE,
    "startup_failure": Status.FAILURE,
}
ERRORS = {
    401: "GitHub rejected the token (HTTP 401)",
    403: "The token can't read this repository (HTTP 403)",
    404: "Repository not found, or the token can't see it (HTTP 404)",
}
LIMITED = (403, 429)
DEFAULT_BACKOFF = timedelta(minutes=1)
MAX_PAGES = 5
NEXT_LINK = re.compile(r'<([^>]+)>\s*;\s*rel="next"')

Run = Mapping[str, Any]
Clock = Callable[[], datetime]


class GitHubError(ValueError):
    pass


class RateLimited(FetchError):
    def __init__(self, until: datetime):
        super().__init__(f"GitHub rate limit reached, retrying after {until.astimezone():%H:%M}")
        self.until = until


class RateLimits:
    """Remembers, per token, when GitHub said to call again, so polls before then make no request."""

    def __init__(self, clock: Clock = lambda: datetime.now(UTC)):
        self.clock = clock
        self.until: dict[str, datetime] = {}

    def check(self, key: str) -> None:
        until = self.until.get(key)
        if until is not None and self.clock() < until:
            raise RateLimited(until)

    def record(self, key: str, response: Response) -> datetime | None:
        until = blocked_until(response, self.clock())
        if until is None:
            self.until.pop(key, None)
        else:
            self.until[key] = until
        return until


def blocked_until(response: Response, now: datetime) -> datetime | None:
    retry_after = response.headers.get("retry-after", "")
    if response.status in LIMITED and retry_after.isdigit():
        return now + timedelta(seconds=int(retry_after))
    reset = response.headers.get("x-ratelimit-reset", "")
    if response.headers.get("x-ratelimit-remaining") == "0" and reset.isdigit():
        return datetime.fromtimestamp(int(reset), UTC)
    if response.status == 429 or (response.status == 403 and b"rate limit" in response.body.lower()):
        return now + DEFAULT_BACKOFF
    return None


class GitHubSource:
    def __init__(
        self,
        server: ServerSettings,
        timeout: float | None,
        connection: Connection,
        rate_limits: RateLimits,
        apply_excludes: bool = True,
    ):
        self.server = server
        self.timeout = timeout
        self.connection = connection
        self.rate_limits = rate_limits
        self.apply_excludes = apply_excludes

    def fetch(self) -> list[Project]:
        projects = [self.to_project(runs) for runs in group(self.filtered(self.read_pages()))]
        if not self.apply_excludes:
            return projects
        return [project for project in projects if project.name not in self.server.excluded_projects]

    def read_pages(self) -> list[Run]:
        """Older pages too, a few at most, until the filtered runs include a finished one."""
        runs: list[Run] = []
        url = self.runs_url()
        for _ in range(MAX_PAGES):
            response = self.get(url)
            runs += read_runs(response.body)
            following = next_page(response)
            if following is None or any(run.get("status") == "completed" for run in self.filtered(runs)):
                break
            url = following
        return runs

    def get(self, url: str) -> Response:
        self.rate_limits.check(self.rate_key())
        response = self.connection.request(url, self.timeout, self.headers(), self.verify())
        self.raise_for_status(response)
        return response

    def runs_url(self) -> str:
        query = {"per_page": "100"} | ({"branch": self.server.branch} if self.server.branch else {})
        return f"{API}/repos/{self.server.repository}/actions/runs?{urlencode(query)}"

    def headers(self) -> dict[str, str]:
        token = self.server.password
        return HEADERS | ({"Authorization": f"Bearer {token}"} if token else {})

    def rate_key(self) -> str:
        """GitHub meters by token, or by address without one. The key holds a digest, never the token."""
        token = self.server.password
        return f"{API} " + (hashlib.sha256(token.encode()).hexdigest() if token else "anonymous")

    def verify(self) -> bool:
        return not self.server.skip_ssl_verification

    def raise_for_status(self, response: Response) -> None:
        until = self.rate_limits.record(self.rate_key(), response)
        if response.status == 200:
            return
        if until is not None and response.status in LIMITED:
            raise RateLimited(until)
        raise FetchError(ERRORS.get(response.status, f"GitHub returned HTTP {response.status}"), response.status)

    def filtered(self, runs: list[Run]) -> list[Run]:
        runs = [run for run in runs if not is_dynamic(run)]
        workflow = self.server.workflow
        if not workflow:
            return runs
        return [run for run in runs if workflow in (run.get("name"), str(run.get("path", "")).rpartition("/")[2])]

    def to_project(self, runs: list[Run]) -> Project:
        latest = runs[0]
        finished = next((run for run in runs if run.get("status") == "completed"), None)
        time = str(finished.get("updated_at") or "") if finished else ""
        return Project(
            server_url=self.server.url,
            name=f"{latest.get('name')} ({latest.get('head_branch')})",
            status=CONCLUSIONS.get(str(finished.get("conclusion")), Status.UNKNOWN) if finished else Status.UNKNOWN,
            activity=Activity.SLEEPING if latest.get("status") == "completed" else Activity.BUILDING,
            url=str(latest.get("html_url", "")),
            last_build_time=time,
            build_time=parse_build_time(time, NONE_TIMEZONE),
            last_build_label=str(finished.get("run_number")) if finished else None,
            prefix=self.server.prefix or self.server.repository.rpartition("/")[2] or None,
        )


def is_dynamic(run: Run) -> bool:
    """Dependabot and similar dynamic runs: one per update, with the run number in the name."""
    return run.get("event") == "dynamic" or str(run.get("path", "")).startswith("dynamic/")


def next_page(response: Response) -> str | None:
    """The rel="next" link, if it points at the GitHub API, so the token is never sent anywhere else."""
    match = NEXT_LINK.search(response.headers.get("link", ""))
    if match is None or not match.group(1).startswith(f"{API}/"):
        return None
    return match.group(1)


def read_runs(body: bytes) -> list[Run]:
    try:
        runs = json.loads(body)["workflow_runs"]
    except (ValueError, KeyError, TypeError) as ex:
        raise GitHubError("Not a GitHub workflow runs response") from ex
    if not isinstance(runs, list):
        raise GitHubError("Not a GitHub workflow runs response")
    return runs


def group(runs: list[Run]) -> list[list[Run]]:
    """Runs grouped by workflow and branch, newest first, in the order each group first appears."""
    groups: dict[tuple[Any, Any], list[Run]] = {}
    for run in runs:
        groups.setdefault((run.get("workflow_id"), run.get("head_branch")), []).append(run)
    return list(groups.values())
