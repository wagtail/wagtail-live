import factory
import wagtail_factories

from tests.testapp.models import BlogPage


class BlogPageFactory(wagtail_factories.PageFactory):
    title = factory.Sequence(lambda n: "Page {}".format(n))
    channel_id = factory.Sequence(lambda n: "channel-{}".format(n))

    class Meta:
        model = BlogPage
