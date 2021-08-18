from wagtail_live.version import get_complete_version, get_version


def test_get_version_not_final():
    assert get_version((1, 0, 0, "alpha", 1)) == "1.0a1"


def test_get_version_final():
    assert get_version((1, 0, 0, "final", 1)) == "1.0"


def test_get_complete_version():
    from wagtail_live import VERSION

    assert get_complete_version() == VERSION
