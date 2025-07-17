from celery import Celery
from stalk import celeryconfig
app = Celery('Celery_MetalmageAI')
app.config_from_object(celeryconfig)
