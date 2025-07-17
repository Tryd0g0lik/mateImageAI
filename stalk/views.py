from celery import Celery
app = Celery('Celery_MetalmageAI')
app.config_from_object('./celeryconfig')
