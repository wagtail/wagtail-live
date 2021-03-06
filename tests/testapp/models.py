from wagtail.core.models import Page

from wagtail_live.models import LivePageMixin


class BlogPage(LivePageMixin, Page):
    content_panels = Page.content_panels + LivePageMixin.panels


class RegularPage(Page):
    pass
