from .version import get_version

# major.minor.patch.release.number
# release must be one of alpha, beta, rc, or final
VERSION = (1, 0, 0, "alpha", 2)

__version__ = get_version(VERSION)
