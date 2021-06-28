import sys
from importlib import reload

from django.urls import clear_url_caches


def reload_urlconf():
    clear_url_caches()
    for module in ["wagtail_live.urls", "tests.urls"]:
        if module in sys.modules:
            reload(sys.modules[module])
