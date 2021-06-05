from django.urls import path
from .views import DebugView

urlpatterns = [
    path("debug/", DebugView.as_view(), name="debug")
]
