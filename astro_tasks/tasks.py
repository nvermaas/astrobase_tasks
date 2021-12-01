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
    number_of_jobs = services.get_number_of_jobs()
    result = "get_jobs() from " + current_task.request.hostname + " = "+str(number_of_jobs)
    return result


# client program to test access to celery/broker
if __name__ == '__main__':

    # use this to test/debug functionality in services,
    # because the debugger doesn't work with @app.tasks
    number_of_jobs = services.get_number_of_jobs()
    print(number_of_jobs)
