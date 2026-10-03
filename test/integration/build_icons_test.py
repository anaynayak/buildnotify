import pytest
from PySide6.QtCore import QSize
from PySide6.QtGui import QColor, QIcon, QImage

from buildnotifylib.ui.build_icons import BADGE_RING, TRAY_SIZE, BuildIcons, badge_label, badge_rect


@pytest.mark.functional
def test_should_consolidate_build_status(qtbot):
    aggregate_status = BuildIcons().for_aggregate_status("Success.Sleeping", 0)
    assert aggregate_status is not None


@pytest.mark.functional
def test_should_consolidate_build_status_with_failure_count(qtbot):
    aggregate_status = BuildIcons().for_aggregate_status("Success.Building", 1)
    assert aggregate_status is not None


@pytest.mark.functional
@pytest.mark.parametrize("status", [*BuildIcons().all_status, "Unknown.Status"])
@pytest.mark.parametrize("symbolic", [False, True])
def test_should_load_fallback_icon_from_package_data(qtbot, status, symbolic):
    icons = BuildIcons()
    assert not icons.fallback(icons.icon_name(status, symbolic)).isNull()


def test_should_name_symbolic_icons_with_the_freedesktop_suffix():
    icons = BuildIcons()

    assert icons.icon_name("Failure.Building", symbolic=True) == "buildnotify-failure-building-symbolic"
    assert icons.icon_name("Unknown.Status", symbolic=True) == "buildnotify-inactive-symbolic"
    assert icons.icon_name("Failure.Building") == "buildnotify-failure-building"


def shape(icon: QIcon) -> QImage:
    return icon.pixmap(QSize(22, 22)).toImage().convertToFormat(QImage.Format.Format_Alpha8)


@pytest.mark.functional
def test_should_tell_symbolic_icons_apart_by_shape_alone(qtbot):
    icons = BuildIcons()
    names = sorted(set(icons.all_status.values()))
    shapes = [shape(icons.fallback(f"{name}-symbolic")) for name in names]

    assert all(a != b for i, a in enumerate(shapes) for b in shapes[i + 1 :])


@pytest.mark.functional
def test_should_keep_symbolic_icons_sharp_on_hidpi(qtbot):
    icons = BuildIcons()

    assert icons.fallback("buildnotify-failure-symbolic").availableSizes()[0].width() >= 88


@pytest.mark.functional
def test_should_draw_the_count_over_a_symbolic_icon(qtbot):
    icon = BuildIcons().for_aggregate_status("Failure.Sleeping", 2, 2.0, symbolic=True)

    assert icon.availableSizes() == [QSize(44, 44)]


@pytest.fixture
def theme(tmp_path):
    theme_dir = tmp_path / "testtheme"
    (theme_dir / "scalable").mkdir(parents=True)
    (theme_dir / "index.theme").write_text(
        "[Icon Theme]\nName=testtheme\nDirectories=scalable\n\n[scalable]\nSize=22\nType=Scalable\n"
    )
    for name in ("buildnotify-failure", "buildnotify-success-symbolic"):
        (theme_dir / "scalable" / f"{name}.svg").write_text(
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
    assert BuildIcons().for_status("Success.Sleeping", symbolic=True).name() == "buildnotify-success-symbolic"


@pytest.mark.functional
def test_should_not_swap_a_missing_symbolic_theme_icon_for_the_coloured_one(qtbot, theme):
    assert BuildIcons().for_status("Failure.Sleeping", symbolic=True).name() == ""
    assert BuildIcons().for_status("Success.Sleeping").name() == ""


@pytest.mark.functional
@pytest.mark.parametrize("ratio, pixels", [(1.0, 22), (2.0, 44), (1.5, 33)])
def test_should_render_the_count_overlay_at_the_device_pixel_ratio(qtbot, ratio, pixels):
    icon = BuildIcons().for_aggregate_status("Failure.Sleeping", 2, device_pixel_ratio=ratio)

    assert icon.availableSizes() == [QSize(pixels, pixels)]


@pytest.mark.functional
def test_should_draw_the_count_over_the_status_icon(qtbot):
    icons = BuildIcons()
    plain = icons.for_status("Failure.Sleeping").pixmap(QSize(22, 22), 2.0).toImage()
    counted = icons.for_aggregate_status("Failure.Sleeping", 3, device_pixel_ratio=2.0).pixmap(QSize(22, 22), 2.0)

    assert counted.toImage() != plain


@pytest.mark.parametrize("ratio", [1.0, 1.5, 2.0])
@pytest.mark.parametrize("count", [1, 12, 345])
def test_should_fit_the_badge_in_the_bottom_right_corner(ratio, count):
    rect = badge_rect(count, ratio)

    assert rect.right() == TRAY_SIZE.width() and rect.bottom() == TRAY_SIZE.height()
    assert rect.left() >= 0 and rect.height() >= TRAY_SIZE.height() / 2
    assert rect.width() >= rect.height()


@pytest.mark.parametrize("ratio", [1.0, 1.5, 2.0])
def test_should_snap_the_badge_to_whole_device_pixels(ratio):
    rect = badge_rect(7, ratio)

    for edge in (rect.left(), rect.top(), rect.width(), rect.height()):
        assert (edge * ratio).is_integer()


def test_should_widen_the_badge_for_more_digits():
    assert badge_rect(1, 1.0).width() < badge_rect(12, 1.0).width() < badge_rect(345, 1.0).width()


def test_should_cap_the_badge_label():
    assert badge_label(7) == "7"
    assert badge_label(99) == "99"
    assert badge_label(100) == "99+"


def pixel(icon: QIcon, x: float, y: float, ratio: float) -> QColor:
    return icon.pixmap(TRAY_SIZE, ratio).toImage().pixelColor(int(x * ratio), int(y * ratio))


@pytest.mark.functional
@pytest.mark.parametrize("symbolic", [False, True])
@pytest.mark.parametrize("ratio", [1.0, 2.0])
def test_should_leave_the_icon_centre_clear_of_the_badge(qtbot, symbolic, ratio):
    icons = BuildIcons()
    plain = icons.for_status("Failure.Sleeping", symbolic)
    counted = icons.for_aggregate_status("Failure.Sleeping", 3, ratio, symbolic=symbolic)

    assert pixel(counted, 10.5, 10.5, ratio) == pixel(plain, 10.5, 10.5, ratio)
    assert pixel(counted, 5, 5, ratio) == pixel(plain, 5, 5, ratio)


@pytest.mark.functional
@pytest.mark.parametrize("symbolic", [False, True])
def test_should_knock_out_a_ring_around_the_badge(qtbot, symbolic):
    counted = BuildIcons().for_aggregate_status("Failure.Sleeping", 3, 2.0, symbolic=symbolic)
    rect = badge_rect(3, 2.0)
    ring = pixel(counted, int(rect.center().x()), rect.top() - BADGE_RING / 2, 2.0)

    assert ring.alpha() == 0


@pytest.mark.functional
def test_should_tell_colour_icons_apart_by_building_state(qtbot):
    icons = BuildIcons()

    def image(name):
        return icons.fallback(name).pixmap(TRAY_SIZE).toImage()

    for colour in ("success", "failure"):
        assert image(f"buildnotify-{colour}") != image(f"buildnotify-{colour}-building")


def test_should_use_a_different_icon_for_unreachable_than_for_unknown():
    icons = BuildIcons()

    assert icons.icon_name("unreachable") == "buildnotify-unreachable"
    assert icons.icon_name("unreachable") != icons.icon_name(None)
    assert icons.icon_name("unreachable", symbolic=True) == "buildnotify-unreachable-symbolic"


@pytest.mark.functional
def test_should_tell_unreachable_from_unknown_in_both_icon_sets(qtbot):
    icons = BuildIcons()

    for suffix in ("", "-symbolic"):
        unknown = icons.fallback(f"buildnotify-inactive{suffix}").pixmap(TRAY_SIZE).toImage()
        unreachable = icons.fallback(f"buildnotify-unreachable{suffix}").pixmap(TRAY_SIZE).toImage()
        assert unknown != unreachable
