import os
import re
import time
import requests
from django.conf import settings
from cloudsek import celery_app
from celery import current_task
from celery.result import AsyncResult
from django.core.files import File
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from file_downloader.models import FileData


def send_status_via_socket(status):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'task_result',
        {'type': 'result', 'result': status}
    )


@celery_app.task()
def download_file(url):
    task_id = current_task.request.id
    time.sleep(5)
    file_obj = FileData.objects.get(task_id=task_id)
    response = requests.get(url, stream=True)
    _temp = response.headers.get('content-disposition')
    file_name = url.split('/')[-1]
    print(file_name, '1', _temp)
    if _temp:
        file_name = re.findall('filename="(.+)"', _temp)
        print(file_name)
        if isinstance(file_name, list):
            file_name = file_name[-1]
    total_length = response.headers.get('content-length')
    print(file_name)
    file_obj.total_file_size = total_length/1000000
    file_obj.file_name = file_name
    file_obj.save()

    download_location = os.path.join(settings.BASE_DIR, settings.MEDIA_ROOT)
    file_path = os.path.join(download_location, file_name)

    downloaded = 0
    status = {}
    with open(file_path, "wb") as f:
        print("Downloading %s" % file_name)
        start = time.clock()
        if total_length is None:
            f.write(response.content)
        else:
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                f.write(data)
                downloaded += len(data)
                status = {
                        'total_file_size': '%.2f Mb' % (total_length/1000000),
                        'downloaded': '%.2f Mb' % (downloaded/1000000),
                        'pending': '%.2f Mb' % ((total_length - downloaded)/1000000),
                        'status': 'Downloading',
                        'speed': '%.2f Mb/s' % ((downloaded//(time.clock() - start))/1000000),
                        'task_id': task_id,
                        'file_name': file_name,
                        'is_downloading': file_obj.is_downloading
                    }
                current_task.update_state(
                    state="pending",
                    meta=status)
                send_status_via_socket(status)
    file_obj.downloaded_file.save(file_name, File(open(file_path, "rb")))
    file_obj.downloaded_file_size = downloaded/1000000
    file_obj.is_downloading = False
    file_obj.status = 'Downloaded'
    file_obj.save()
    status.update({
        'status': 'Downloaded',
        'speed': '0 Mb/s',
        'task_id': task_id,
        'file_name': file_name,
        'is_downloading': file_obj.is_downloading,
        'file_url': file_obj.downloaded_file.url
    })
    current_task.update_state(
        state="Completed",
        meta=status
    )
    send_status_via_socket(status)
    return 'Done'
