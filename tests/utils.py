import sys
from importlib import reload
from io import BytesIO

import PIL.Image
from django.core.files.images import ImageFile
from django.urls import clear_url_caches


def reload_urlconf():
    clear_url_caches()
    for module in ["wagtail_live.urls", "tests.urls"]:
        if module in sys.modules:
            reload(sys.modules[module])


def get_test_image_file(filename, size, colour="white"):
    # Copied from wagtail.images.tests.utils

    f = BytesIO()
    image = PIL.Image.new("RGBA", size, colour)
    image.save(f, "PNG")
    return ImageFile(f, name=filename)
