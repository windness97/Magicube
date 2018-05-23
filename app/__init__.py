from flask import Flask
from celery import Celery, current_app
import os
from MagicCube.main_flask import init_cubemanager

app_path = os.path.dirname(__file__)

app = Flask(__name__)
app.config['CELERY_BROKE_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKE_URL'], bckend=app.config['CELERY_RESULT_BACKEND'])
celery.conf.update(app.config)

current_app.conf.CELERY_ALWAYS_EAGER = True
current_app.conf.CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

init_cubemanager()

from app import views
