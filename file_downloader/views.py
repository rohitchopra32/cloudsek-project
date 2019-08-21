from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from django.contrib.auth.models import User
from file_downloader.tasks import download_file
from celery.result import AsyncResult
from celery.app.control import Control
from cloudsek.celery import app
from file_downloader.models import FileData
from django.db.models import F


class FileDownloaderApi(APIView):
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request, pk=None):
        if pk:
            print(pk)
            result = AsyncResult(pk)
            print(result.status, result.info, result.state)
            return Response({'Worked': 'Hekllo', 'status': result.info, 'id': pk}, template_name='index.html')
        all_tasks = FileData.objects.filter().annotate(pending=F('total_file_size') - F('downloaded_file_size'))

        return Response({'Worked': 'Hello', 'tasks': all_tasks}, template_name='index.html')


@api_view(['GET'])
def stop(request, task_id=None):
    control = Control(app=app)
    control.revoke(task_id, terminate=True)
    file_obj = FileData.objects.get(task_id=task_id)
    file_obj.status = 'Canceled'
    file_obj.save()
    return Response({'success': True}, status=200)


@api_view(['POST'])
def upload_url(request):
    url = request.data.get('url', '')
    task_id = download_file.delay(url)
    FileData.objects.create(task_id=task_id.id)
    return Response({'Worked': url, 'id': task_id.id}, content_type='application/json')
