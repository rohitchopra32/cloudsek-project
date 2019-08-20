import re
import time
import requests
from cloudsek import celery_app
from celery import current_task


@celery_app.task()
def download_file(url):
    response = requests.get(url, stream=True)
    _temp = response.headers.get('content-disposition')
    file_name = url.split('/')[-1]
    if _temp:
        file_name = re.findall("filename=(.+)", _temp)
    total_length = response.headers.get('content-length')
    print('\n', total_length, ' ----> Total Size')

    with open(file_name, "wb") as f:
        print("Downloading %s" % file_name)
        start = time.clock()
        if total_length is None:
            f.write(response.content)
        else:
            downloaded = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                downloaded += len(data)
                f.write(data)
                current_task.update_state(
                    state="pending",
                    meta={
                        'total_file_size': total_length,
                        'downloaded': downloaded,
                        'pending': total_length - downloaded,
                        'status': 'Downloading',
                        'speed': '{} Bps'.format(downloaded//(time.clock() - start)),
                    })

    return 'Done'
