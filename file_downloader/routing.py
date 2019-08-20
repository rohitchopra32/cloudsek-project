from django.urls import path

from . import consumer

websocket_urlpatterns = [
    path('ws/<slug:task_id>/', consumer.SendFileStatus),
]
