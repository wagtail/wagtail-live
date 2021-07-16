""" Webapp URLs """

from django.urls import include, path

from . import views

api_patterns = [
    path("channels/", views.create_channel_view),
    path("channels/<slug:channel_name>/", views.delete_channel_view),
    path("messages/", views.create_message_view),
    path("messages/<int:pk>/", views.message_detail_view),
    path("images/<int:pk>/", views.delete_image_view),
]

urlpatterns = [
    path("api/", include(api_patterns)),
    path("channels/", views.channels_list_view, name="channels"),
    path(
        "channels/<slug:channel_name>/",
        views.channel_detail_view,
        name="channel_detail",
    ),
]
