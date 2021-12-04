import os
from os import listdir
from celery import current_task
from my_celery import app
from astro_tasks import services

try:
    ASTROBASE_URL = os.environ['ASTROBASE_URL']
except:
    ASTROBASE_URL = "http://localhost:8000/my_astrobase/"


@app.task
def ping(name):
    # demo task to see if this can be reached from Django
    return "ponggg " + name + " from " + current_task.request.hostname


@app.task
def dir(my_path):
    return listdir(my_path)


@app.task
def get_jobs():
    # look for pending jobs in astrobase

    # get this function as empty as possible (because debugger doesn't work here).
    print(current_task.request.hostname)
    return services.get_jobs_from_astrobase('astro')


def get_jobs_test():
    return services.get_jobs_from_astrobase('astro')


# client program to test access to celery/broker
if __name__ == '__main__':

    # use this to test/debug functionality in services,
    # because the debugger doesn't work with @app.tasks

    # execute my_astro_worker.bat to start a local worker, then run/debug this file
    ids = get_jobs_test()
    print(ids)
