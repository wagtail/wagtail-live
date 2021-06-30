""" Webapp URLs """

from django.urls import include, path

from . import views

api_patterns = [
    path("channels/", views.DummyChannelListAPIView.as_view()),
    path("channels/<slug:channel_name>/", views.DummyChannelDetailAPIView.as_view()),
    path("messages/", views.MessageListAPIView.as_view()),
    path("messages/<int:pk>/", views.MessageDetailAPIView.as_view()),
]

urlpatterns = [
    path(
        "channels/",
        views.DummyChannelListView.as_view(),
        name="channels",
    ),
    path(
        "channels/<slug:channel_name>/",
        views.DummyChannelDetailView.as_view(),
        name="channel_detail",
    ),
    path("api/", include(api_patterns)),
]
