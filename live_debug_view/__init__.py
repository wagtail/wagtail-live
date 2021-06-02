""" Wagtail Live Debug View.

Wagtail Live Debug view is a debugging tool that mimics a chat app.
It provides a DummyChannel interface where the user can post Messages.

To use it, first add it to INSTALLED_APPS in your settings file:

INSTALLED_APPS = [
    ...
    'live_debug_view',
    ...
]

Then, run python manage.py makemigrations --> python manage.py migrate
to make migrations for the debug view models i.e DummyChannel and Message.

Finally, hook the 'live debug view' URLs like this:

from live_debug_view imports urls as debug_view_urls

urlpatterns += [
    path("live_debug_view/", include(debug_view_urls)),
]

Start the development server and head to http://localhost:8000/live_debug_view/.

From there, you can create/delete dummy channels.
In a dummy channel page, you can add/edit/delete messages.

This is intended for development use only.
"""
