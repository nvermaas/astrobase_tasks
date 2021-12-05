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
    return "ponggg " + name + " from " + str(current_task.request.hostname)

@app.task(name='astro_task.tasks.ping2')
def ping2(name):
    # demo task to see if this can be reached from Django
    return "ponggg " + name + " from " + str(current_task.request.hostname)

@app.task
def dir(my_path):
    return listdir(my_path)


@app.task
def handle_job(id):
    # get this function as empty as possible (because debugger doesn't work here).
    return services.handle_job(id)

def handle_job_test(id):
    # get this function as empty as possible (because debugger doesn't work here).
    return services.handle_job(id)


@app.task
def get_jobs():
    # look for pending jobs in astrobase

    # get this function as empty as possible (because debugger doesn't work here).
    return services.get_jobs_from_astrobase('astro')

def get_jobs_test():
    return services.get_jobs_from_astrobase('astro')




# client program to test access to celery/broker
if __name__ == '__main__':

    # use this to test/debug functionality in services,
    # because the debugger doesn't work with @app.tasks

    # execute my_astro_worker.bat to start a local worker, then run/debug this file
    # this works, all jobs are delivered at once... (then handled 1 by 1)
    #ids = get_jobs_test()

    #handle_job_test("335")
    task = app.send_task("astro_tasks.tasks.get_jobs")
    print(task.get())

    task = app.send_task("astro_tasks.tasks.ping", kwargs=dict(name="my remote app"))
    print(task.get())  # pong my remote app

    #task = app.send_task("astro_tasks.tasks.handle_job", kwargs=dict(id="346"))
    #task = app.send_task("astro_tasks.tasks.handle_job", kwargs=dict(id="347"))
    #task = app.send_task("astro_tasks.tasks.handle_job", kwargs=dict(id="348"))
    # print(task.get())

    print('run has finished')