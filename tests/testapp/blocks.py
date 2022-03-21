from wagtail.core.blocks import CharBlock, StructBlock

from wagtail_live.blocks import LivePostBlock


class CustomLivePostBlock(LivePostBlock):
    posted_by = CharBlock(required=False)


class CustomBlock(StructBlock):
    pass
