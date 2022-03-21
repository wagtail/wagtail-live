import sys
from functools import wraps
from importlib import reload
from io import BytesIO

import PIL.Image
from django.core.files.base import File
from django.urls import clear_url_caches


def reload_urlconf():
    clear_url_caches()
    for module in ["wagtail_live.urls", "tests.urls"]:
        if module in sys.modules:
            reload(sys.modules[module])


def get_test_image_file(filename="test.png", size=(100, 100), colour="white"):
    f = BytesIO()
    image = PIL.Image.new("RGBA", size, colour)
    image.save(f, "PNG")
    f.seek(0)
    return File(f, name=filename)


class clear_function_cache_before_and_after_execution:
    def __init__(self, cached_func):
        self.cached_func = cached_func

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.cached_func.cache_clear()
            exception = None

            try:
                func(*args, **kwargs)
            except Exception as e:
                exception = e
            finally:
                self.cached_func.cache_clear()

            if exception:
                raise exception

        return wrapper
