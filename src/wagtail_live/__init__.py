from .version import get_version

# major.minor.patch.release.number
# release must be one of alpha, beta, rc, or final
VERSION = (1, 0, 0, "alpha", 3)

__version__ = get_version(VERSION)

# For compatibility with Django < 3.2
default_app_config = "wagtail_live.apps.WagtailLiveConfig"
