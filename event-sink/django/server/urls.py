from django.urls import path
from . import views

urlpatterns = [
    path("api/EventSink/", views.eventsink, name="sink"),
    path("clean/", views.cleandb, name="clean"),
]
