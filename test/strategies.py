from hypothesis import strategies as st

from buildnotifylib.core.model import Activity, Project, Status

ANY_STATUS = st.sampled_from(Status)
ANY_ACTIVITY = st.sampled_from(Activity)


def projects(status=ANY_STATUS, activity=ANY_ACTIVITY):
    return st.builds(
        Project,
        server_url=st.sampled_from(["s1", "s2"]),
        name=st.text(max_size=5),
        status=status,
        activity=activity,
        url=st.just("http://x"),
        last_build_time=st.sampled_from(["", "2009-05-29T13:54:07"]),
        last_build_label=st.sampled_from([None, "1", "2"]),
    )


def project_lists(status=ANY_STATUS, activity=ANY_ACTIVITY):
    return st.lists(projects(status, activity), max_size=6)


def unique_project_lists():
    return st.lists(projects(), max_size=6, unique_by=lambda p: (p.server_url, p.name))
