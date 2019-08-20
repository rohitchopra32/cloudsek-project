from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from django.contrib.auth.models import User
from file_downloader.tasks import download_file
from celery.result import AsyncResult

class FileDownloaderApi(APIView):
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request, pk=None):
        if pk:
            print(pk)
            result = AsyncResult(pk)
            print(result.status, result.info, result.state)
        return Response({'Worked': 'Hekllo', 'status': result.info}, template_name='index.html')

    def post(self, request):
        url = request.data.get('url', '')
        task_id = download_file.delay(url)
        return Response({'Worked': url, 'id': task_id}, template_name='index.html')
