from kombu import Exchange, Queue

broker_url = "redis://83.166.245.209:6380/0"
result_backend = "redis://83.166.245.209:6380/1"


task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
timezone = "Asia/Krasnoyarsk"
enable_utc = True

# celery speed for handle of tasks
# task_annotations = {
#     'one_tasks.celery_task_money': {'rate_limit': '10/m'}
# }

# THe True when need the sync
task_always_eager = False

# quantity of workers
worker_concurrency = 4

"""
 False, чтобы избежать автоматического создания очередей. Это \
 будет эквивалентно использованию `passive=True` из \
 (для методов channel.exchange_declare и channel.queue_declare), \
 так как Celery не будет пытаться создать очереди, если они \
 не существуют. \
"""
# task_exchange = (
#     Exchange('generations', type='direct', passive=True,
#              routing_key='hard')
# )
# task_queues = (
#     Queue('generations', Exchange('generations', type='direct', passive=True),
#           routing_key='hard'),
# )
task_acks_late = True
