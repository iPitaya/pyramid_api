from celery import Celery
from hichao.base.config import CELERY_BROKER_URL
celery = Celery(broker=CELERY_BROKER_URL)
celery.conf.CELERY_TASK_SERIALIZER = 'json'
celery.conf.CELERY_RESULT_SERIALIZER = 'json'
