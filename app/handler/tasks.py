import os
import time
from werkzeug.utils import secure_filename
from app import celery
from app import app_path
from MagicCube.main_flask import excute_frame, refresh_data, update_data
import requests


@celery.task
def logAfter(time):
    print('celery task: log')


@celery.task
def repeatLogging(contentstr, repeatTimes):
    for i in range(0, repeatTimes):
        print("celery task: %s" % contentstr)
        time.sleep(1)


@celery.task(bind=True)
def askForResult(self):
    total = 10
    for i in range(total):
        print("ask for result: %s" % i)
        self.update_state(state='PROGRESS', meta={'current': i, 'total': total, 'status': 'no thing special'})
        time.sleep(1)

    return {'current': total, 'total': total, 'status': 'done', 'result': 233}


# @celery.task(bind=True)
# def save_pic_recog_pic(self, file):
#     # 去除文件名中不合法的内容
#     filename = secure_filename(file.filename)
#     fullname = os.path.join(app_path, 'pictures', filename)
#     file.save(fullname)
# 
#     self.update_state(state='PIC_SAVED')
# 
#     # start the recognition
#     excute_frame(fullname)


@celery.task(bind=True)
def recognize(self, filename):
    # start the recognition
    cubemanager = excute_frame(filename)

    # return cubemanager

@celery.task(bind=True)
def refresh_cube(self):
    refresh_data()

@celery.task(bind=True)
def update_cube(self, data):
    update_data(data)

