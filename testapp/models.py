from wagtail.core.models import Page

from wagtail_live.models import LivePageMixin


class LiveBlogPage(LivePageMixin, Page):
    content_panels = Page.content_panels + LivePageMixin.panels
