from wagtail_live.models import LivePageMixin
from wagtail.core.models import Page


class BlogPage(LivePageMixin, Page):
    content_panels = Page.content_panels + LivePageMixin.panels
