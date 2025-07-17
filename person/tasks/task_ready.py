
"""
person/tasks/task_ready.py
"""
import threading


def  ready(run_async_ofTask):
    """

    :param run_async_ofTask:
    :return:
    """

    thred = threading.Thread(target=run_async_ofTask)
    thred.deamon = True
    thred.start()

