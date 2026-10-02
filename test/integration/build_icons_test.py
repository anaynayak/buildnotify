import pytest
from PySide6.QtGui import QIcon

from buildnotifylib.ui.build_icons import BuildIcons


@pytest.mark.functional
def test_should_consolidate_build_status(qtbot):
    aggregate_status = BuildIcons().for_aggregate_status("Success.Sleeping", "0")
    assert aggregate_status is not None


@pytest.mark.functional
def test_should_consolidate_build_status_with_failure_count(qtbot):
    aggregate_status = BuildIcons().for_aggregate_status("Success.Building", "1")
    assert aggregate_status is not None


@pytest.mark.functional
@pytest.mark.parametrize("status", [*BuildIcons().all_status, "Unknown.Status"])
def test_should_load_fallback_icon_from_package_data(qtbot, status):
    icons = BuildIcons()
    assert not icons.fallback(icons.icon_name(status)).isNull()


@pytest.fixture
def theme(tmp_path):
    theme_dir = tmp_path / "testtheme"
    (theme_dir / "scalable").mkdir(parents=True)
    (theme_dir / "index.theme").write_text(
        "[Icon Theme]\nName=testtheme\nDirectories=scalable\n\n[scalable]\nSize=22\nType=Scalable\n"
    )
    (theme_dir / "scalable" / "buildnotify-failure.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22"><rect width="22" height="22"/></svg>'
    )
    paths, name = QIcon.themeSearchPaths(), QIcon.themeName()
    QIcon.setThemeSearchPaths([str(tmp_path)])
    QIcon.setThemeName("testtheme")
    yield
    QIcon.setThemeSearchPaths(paths)
    QIcon.setThemeName(name)


@pytest.mark.functional
def test_should_prefer_theme_icon_over_fallback(qtbot, theme):
    assert BuildIcons().for_status("Failure.Sleeping").name() == "buildnotify-failure"
    assert BuildIcons().for_status("Success.Sleeping").name() == ""
