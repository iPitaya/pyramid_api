from hichao.base.config import CELERY_BROKER_URL

CELERY_IMPORT = (
    "hichao.collect.models.collect",
    "hichao.base.celery.favor",
    "hichao.user.views.device",
    "hichao.points.models.points",
    "hichao.comment.views.sub_thread",
    "hichao.forum.views.thread"
)

BROKER_URL = CELERY_BROKER_URL
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_IMPORTS = CELERY_IMPORT
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
