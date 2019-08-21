from django.urls import path
from file_downloader.views import FileDownloaderApi
from file_downloader.views import stop
from file_downloader.views import upload_url

urlpatterns = [

    path("upload-url/", upload_url, name="upload_url"),
    path("<slug:task_id>/stop/", stop, name="stop"),
    path("<slug:pk>/", FileDownloaderApi.as_view(), name="get detail"),
    path("", FileDownloaderApi.as_view()),
]
