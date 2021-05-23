from wagtail.core.models import Page

from wagtail_live.models import LivePageMixin


class SimpleLivePage(Page, LivePageMixin):
    """A simple live page."""

    content_panels = Page.content_panels + LivePageMixin.panels
