from django.urls import path
from file_downloader.views import FileDownloaderApi

urlpatterns = [
    path("<slug:pk>/", FileDownloaderApi.as_view(), name="get detail"),
    path("", FileDownloaderApi.as_view()),
]
