import re
import sys
import asyncio
import requests

pause_dict = {}

async def download_file(link):
    response = requests.get(link, stream=True)
    _temp = response.headers.get('content-disposition')
    file_name = link.split('/')[-1]
    if _temp:
        file_name = re.findall("filename=(.+)", _temp)
    total_length = response.headers.get('content-length')
    print('\n', total_length, ' ----> Total Size')
    
    with open(file_name, "wb") as f: 
            print("Downloading %s" % file_name)
            if total_length is None: 
                f.write(response.content) 
            else: 
                downloaded = 0 
                total_length = int(total_length) 
                for data in response.iter_content(chunk_size=4096): 
                    downloaded += len(data) 
                    sys.stdout.write("{} ---> {} \n".format(str(downloaded), file_name) )
                    f.write(data)
                    done = int(100 * downloaded / total_length) 
                    # sys.stdout.writelines("\r[%s%s]" % ('=' * done, ' ' * (100-done)) )     
                    sys.stdout.flush() 

    return


link = "https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz"
link2 = "http://apache-mirror.8birdsvideo.com/spark/spark-2.4.3/spark-2.4.3-bin-hadoop2.7.tgz"
# download_file(link)

# future = asyncio.Future()
loop = asyncio.get_event_loop()

# tasks = [
#     download_file(link),
#     download_file(link2),
# ]
tasks = [
    asyncio.ensure_future(download_file(link)),
    asyncio.ensure_future(download_file(link2)),
]
loop.run_until_complete(asyncio.gather(*tasks))

# loop.run_until_complete(asyncio.wait(tasks))

loop.close()

# loop.run_in_executor(None, download_file, [link])
# loop.run_in_executor(None, download_file, [link2])

# import multiprocessing
# from multiprocessing.pool import ThreadPool
# from time import time as timer

# start = timer()
# results = ThreadPool(2).imap_unordered(download_file, [link, link2])
# pool = multiprocessing.Pool(processes=4) # how much parallelism?
# pool.map(download_file, [link, link2])

# print(f"Elapsed Time: {timer() - start}")
