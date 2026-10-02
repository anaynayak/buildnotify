import subprocess
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from buildnotifylib.core import cctray
from buildnotifylib.core.model import Activity, Status

FIXTURES = Path(__file__).parent.parent / "fixtures" / "cctray"
ECLIPSE = Path(__file__).parent.parent.parent / "data" / "cctray.xml"


@dataclass
class Source:
    url: str = "http://ci/cc.xml"
    prefix: str | None = None
    timezone: str = "None"
    excluded_projects: list[str] = field(default_factory=list)


def summary(data: bytes, source=None):
    return [(p.name, p.status, p.activity, p.last_build_label, p.url) for p in cctray.parse(data, source or Source())]


def test_should_parse_eclipse_feed():
    projects = cctray.parse(ECLIPSE.read_bytes(), Source())
    assert len(projects) == 7
    assert projects[2].name == "ganymaticPack»R3.0-I"
    assert [p.name for p in projects if p.status is Status.FAILURE] == ["orbit-M"]
    assert projects[0].build_time == datetime(2009, 6, 12, 6, 54, 35).astimezone()
    assert projects[0].server_url == "http://ci/cc.xml"


def test_should_parse_jenkins_feed():
    assert summary((FIXTURES / "jenkins.xml").read_bytes()) == [
        ("payments-api", Status.SUCCESS, Activity.SLEEPING, "1287", "https://jenkins.example.org/job/payments-api/"),
        (
            "platform » infra-deploy",
            Status.FAILURE,
            Activity.BUILDING,
            "96",
            "https://jenkins.example.org/job/platform/job/infra-deploy/",
        ),
        (
            "platform » nightly-e2e",
            Status.FAILURE,
            Activity.SLEEPING,
            "412",
            "https://jenkins.example.org/job/platform/job/nightly-e2e/",
        ),
        ("new-service", Status.UNKNOWN, Activity.SLEEPING, "", "https://jenkins.example.org/job/new-service/"),
    ]


def test_should_ignore_missing_build_time_in_jenkins_feed():
    projects = cctray.parse((FIXTURES / "jenkins.xml").read_bytes(), Source())
    assert projects[0].build_time == datetime(2026, 9, 30, 8, 14, 2, tzinfo=UTC)
    assert projects[3].build_time is None


def test_should_parse_gitlab_feed_with_fractional_offsets():
    projects = cctray.parse((FIXTURES / "gitlab.xml").read_bytes(), Source())
    assert [(p.name, p.get_build_status()) for p in projects] == [
        ("web/storefront:main", "Success.Sleeping"),
        ("web/storefront:release/2.4", "Success.Building"),
        ("data/ingest:main", "Failure.Sleeping"),
    ]
    assert projects[2].build_time.utcoffset() == timedelta(hours=5, minutes=30)


def test_should_parse_gocd_stages_and_jobs_and_skip_messages():
    projects = cctray.parse((FIXTURES / "gocd.xml").read_bytes(), Source())
    assert [(p.name, p.get_build_status(), p.last_build_label) for p in projects] == [
        ("build-linux :: compile", "Success.Sleeping", "214"),
        ("build-linux :: compile :: unit-tests", "Success.Sleeping", "214"),
        ("release :: deploy", "Failure.Building", "57 :: 2"),
        ("release :: deploy :: smoke", "Failure.Building", "57 :: 2"),
    ]


@pytest.mark.parametrize("fixture", ["login-page.html", "broken.xml"])
def test_should_reject_non_cctray_bodies(fixture):
    with pytest.raises(cctray.FeedError):
        cctray.parse((FIXTURES / fixture).read_bytes(), Source())


def test_should_name_the_unexpected_root_element():
    atom = b'<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom"><title>All builds</title></feed>'
    with pytest.raises(cctray.FeedError, match="<feed>"):
        cctray.parse(atom, Source())


@pytest.mark.parametrize("body", [b"", b'<?xml version="1.0"?><Projects><Project name="project" activity='])
def test_should_reject_empty_and_truncated_bodies(body):
    with pytest.raises(cctray.FeedError):
        cctray.parse(body, Source())


def test_should_reject_entity_declarations():
    body = (
        b'<?xml version="1.0"?><!DOCTYPE Projects [<!ENTITY a "aaaaaaaaaa">]>'
        b'<Projects><Project name="&a;" activity="Sleeping"/></Projects>'
    )
    with pytest.raises(cctray.FeedError):
        cctray.parse(body, Source())


def test_should_honour_declared_encoding():
    body = '<?xml version="1.0" encoding="ISO-8859-1"?><Projects><Project name="café"/></Projects>'
    assert [p.name for p in cctray.parse(body.encode("iso-8859-1"), Source())] == ["café"]


def test_should_apply_excludes():
    source = Source(excluded_projects=["orbit-M", "orbit-R"])
    names = [p.name for p in cctray.parse(ECLIPSE.read_bytes(), source)]
    assert len(names) == 5
    assert "orbit-M" not in names and "orbit-R" not in names


def test_should_keep_excluded_projects_on_request():
    source = Source(excluded_projects=["orbit-M"])
    assert len(cctray.parse(ECLIPSE.read_bytes(), source, apply_excludes=False)) == 7


def test_prefix_should_label_but_not_affect_excludes():
    source = Source(prefix="RELEASE", excluded_projects=["orbit-M"])
    labels = [p.label() for p in cctray.parse(ECLIPSE.read_bytes(), source)]
    assert "[RELEASE] orbit-I" in labels
    assert "[RELEASE] orbit-M" not in labels


def attrs(build_time="2009-05-29T13:54:07", **overrides):
    values = {
        "name": "proj1",
        "lastBuildStatus": "Success",
        "activity": "Sleeping",
        "webUrl": "1.2.3.4:8080/cc.xml",
        "lastBuildLabel": "120",
        "lastBuildTime": build_time,
    }
    return values | overrides


def build_time(value, tz="None"):
    return cctray.to_project(attrs(value), Source(timezone=tz)).build_time


def test_should_build_project_from_attributes():
    project = cctray.to_project(attrs(), Source(url="url"))
    assert project.server_url == "url"
    assert project.url == "http://1.2.3.4:8080/cc.xml"
    assert project.last_build_time == "2009-05-29T13:54:07"
    assert project.last_build_label == "120"
    assert project.get_build_status() == "Success.Sleeping"


def test_should_treat_exception_as_failure():
    project = cctray.to_project(attrs(lastBuildStatus="Exception", activity="Building"), Source())
    assert project.status is Status.FAILURE
    assert project.get_build_status() == "Failure.Building"


def test_should_not_override_existing_url_scheme():
    assert cctray.to_project(attrs(webUrl="https://10.0.0.1/project1"), Source()).url == "https://10.0.0.1/project1"


def test_should_ignore_empty_or_garbage_build_time():
    assert build_time("") is None
    assert build_time("not a date", "Asia/Kolkata") is None


@pytest.mark.parametrize(
    "value, tz, offset",
    [
        ("2015-02-14T13:23:20+05:30", "None", timedelta(hours=5, minutes=30)),
        ("2015-02-14T13:25:53Z", "None", timedelta(0)),
        ("2015-02-14T13:27:20.000+0000", "None", timedelta(0)),
        ("2015-02-14T13:23:20+00:00", "None", timedelta(0)),
        ("2015-02-14T13:23:20+05:30", "Etc/GMT-5", timedelta(hours=5, minutes=30)),
        ("2015-02-14T13:25:53Z", "Asia/Kolkata", timedelta(0)),
        ("2015-02-14T13:23:20", "Asia/Kolkata", timedelta(hours=5, minutes=30)),
        ("2015-07-14T13:23:20", "America/New_York", timedelta(hours=-4)),
    ],
)
def test_should_resolve_build_time_offset(value, tz, offset):
    parsed = build_time(value, tz)
    assert parsed.utcoffset() == offset
    assert parsed.replace(tzinfo=None) == datetime.fromisoformat(value).replace(tzinfo=None)


@pytest.mark.parametrize("tz", ["None", "EDT"])
def test_should_fall_back_to_local_time(tz):
    assert build_time("2015-02-14T13:23:20", tz) == datetime(2015, 2, 14, 13, 23, 20).astimezone()


def test_core_model_and_parser_should_not_import_qt_requests_or_keyring():
    code = (
        "import sys, buildnotifylib.core.model, buildnotifylib.core.cctray; "
        "print(sorted(m for m in ('PySide6', 'requests', 'keyring') if m in sys.modules))"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    assert result.stdout.strip() == "[]"
