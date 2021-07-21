<p align="center">

![Wagtail Live](docs/images/wagtail-live-logo.svg)

</p>

# Wagtail Live

_Wagtail Live_ is a Wagtail CMS package to create live blog pages. 

## About

With Wagtail Live:
- Reporters can _instantly publish to a live blog_ by submitting messages via mobile apps.
- Audience can read the posts right away as the live blog page instantly updates. 
- Content editors can edit messages via the Wagtail Admin. The internal format is a normal Wagtail page with streamfield and blocks.
- Create, update, delete operations. 
- Rich text, images, emojis, URLs are converted to embeds.

Slack and a Live blog page:
![Wagtail Live: Slack and live blog page](docs/images/slack-and-live-blog-page.jpg)

Content is also editable via the Wagtail admin:
![Wagtail Live: Page edit view](docs/images/wagtail-admin.jpg)

## Install

    python -m pip install wagtail-live

Add to installed apps:

    INSTALLED_APPS = [
        "wagtail_live",
    ]

Your LiveBlogPage needs to have the LivePageMixin: 

    from wagtail.core.models import Page

    from wagtail_live.models import LivePageMixin

    class LiveBlogPage(LivePageMixin, Page):
        content_panels = Page.content_panels + LivePageMixin.panels

You also need to configure a receiver (messaging app) and publisher (frontend updating technique).

Receivers:

- Slack [Set up Slack Events API Receiver](docs/getting_started/setup_slack.md)
- Telegram
- Webapp
- ...

Publishers:

- Interval polling
- Long polling [Set up long polling publisher](docs/getting_started/setup_long_polling.md)
- ...

## Documentation

[https://wagtail.github.io/wagtail-live/](https://wagtail.github.io/wagtail-live/)

## Google Summer of Code

This project is part of Google Summer of Code 2021 by Tidiane Dia.
