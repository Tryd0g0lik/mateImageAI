from kombu import Exchange, Queue

# sudo docker system prune -a --volumes
# from dotenv_ import (REDIS_LOCATION_URL) #
# from project import settings
# DJANGO_SETTINGS_MODULE=settings

# broker_url = "redis_assistant://83.166.245.209:6380/0"
broker_url = "redis://83.166.245.209:6380/0"
result_backend = "redis://83.166.245.209:6380/0"
# result_backend = f"{REDIS_LOCATION_URL}"


task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
timezone = "Asia/Krasnoyarsk"
enable_utc = True

# celery speed for handle of tesks
# task_annotations = {
#     'one_tasks.celery_task_money': {'rate_limit': '10/m'}
# }

# THe True when need the sync
# task_always_eager = False

# quantity of workers
worker_concurrency = 1

"""
 False, чтобы избежать автоматического создания очередей. Это \
 будет эквивалентно использованию `passive=True` (
   `passive=True` - Этот параметр означает, что Celery не будет пытаться создать exchange/очередь, а будет использовать существующую
 ) из \
 (для методов channel.exchange_declare и channel.queue_declare), \
 так как Celery не будет пытаться создать очереди, если они \
 не существуют. \

  "routing_key='hard'" указываем или в Exchange или в Queue
"""
# task_exchange = (
#     Exchange('person_exchange', type='direct',)
# )
# task_queues = (
#     Queue('person_queue', task_exchange),
# )

# broker_transport_options = {
#     'visibility_timeout': 3600,  # 1 час
#     'socket_timeout': 30,
#     'retry_on_timeout': True,
#     'max_retries': 3,
#     'interval_start': 0,
#     'interval_step': 0.2,
#     'interval_max': 0.5,
# }
worker_prefetch_multiplier = 1  # По умолчанию 4
# worker_max_tasks_per_child = 1  # Перезапуск worker'а после 1 задач


# task_acks_late = True

# broker_connection_retry_on_startup = True # Проверка подключения
