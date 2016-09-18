from test.fake_conf import ConfigBuilder
from buildnotifylib.core.projects import ProjectsPopulator
import pytest

@pytest.mark.functional
def test_should_fetch_projects(qtbot):
    conf = ConfigBuilder().build()
    populator = ProjectsPopulator(conf)
    with qtbot.waitSignal(populator.updated_projects, timeout=1000) as blocker:
        populator.process()



