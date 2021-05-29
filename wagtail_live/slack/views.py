from django.views.decorators.csrf import csrf_exempt
from slack_bolt.adapter.django import SlackRequestHandler

from wagtail_live.slack.app import app

handler = SlackRequestHandler(app=app)


@csrf_exempt
def slack_events_handler(request):
    return handler.handle(request)
