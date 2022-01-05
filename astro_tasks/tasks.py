import os
from os import listdir
from celery import current_task
from my_celery import app, VERSION
from astro_tasks import jobs_controller, registration_controller

try:
    ASTROBASE_URL = os.environ['ASTROBASE_URL']
except:
    ASTROBASE_URL = "http://localhost:8000/my_astrobase/"


@app.task
def ping(name):
    # demo task to see if this can be reached from Django
    return "ponggg " + name + " from " + str(current_task.request.hostname)

@app.task
def dir(my_path):
    return listdir(my_path)

@app.task
def version():
    # get current version
    return "astrobase_tasks version " + VERSION + " from host " + str(current_task.request.hostname)


@app.task
def handle_job(id):
    # get this function as empty as possible (because debugger doesn't work here).
    return jobs_controller.handle_job(id)

def handle_job_test(id):
    # get this function as empty as possible (because debugger doesn't work here).
    return jobs_controller.handle_job(id)

@app.task
def handle_cutout(id):
    # get this function as empty as possible (because debugger doesn't work here).
    return jobs_controller.handle_job(id)

def handle_cutout_test(id):
    # get this function as empty as possible (because debugger doesn't work here).
    return jobs_controller.handle_job(id)

@app.task
def get_jobs():
    # look for pending jobs for the celery service in astrobase

    # get this function as empty as possible (because debugger doesn't work here).
    return jobs_controller.get_jobs_from_astrobase('celery')

def get_jobs_test():
    return jobs_controller.get_jobs_from_astrobase('celery')


@app.task
def registration():
    # get this function as empty as possible (because debugger doesn't work here).
    return registration_controller.handle_registration()

def registration_test():
    # get this function as empty as possible (because debugger doesn't work here).
    return registration_controller.handle_registration()

@app.task
def run_ingest():
    # get this function as empty as possible (because debugger doesn't work here).
    return registration_controller.run_ingest()

def run_ingest_test():
    # get this function as empty as possible (because debugger doesn't work here).
    return registration_controller.run_ingest()

@app.task
def run_submit():
    # get this function as empty as possible (because debugger doesn't work here).
    return registration_controller.run_submit()

def run_submit_test():
    # get this function as empty as possible (because debugger doesn't work here).
    return registration_controller.run_submit()


@app.task
def run_processor():
    # get this function as empty as possible (because debugger doesn't work here).
    return registration_controller.run_processor()

def run_processor_test():
    # get this function as empty as possible (because debugger doesn't work here).
    return registration_controller.run_processor()


@app.task
def run_cleanup():
    # get this function as empty as possible (because debugger doesn't work here).
    return registration_controller.run_cleanup()

def run_cleanup_test():
    # get this function as empty as possible (because debugger doesn't work here).
    return registration_controller.run_cleanup()

# client program to test access to celery/broker
if __name__ == '__main__':

    # use this to test/debug functionality in jobs_controller,
    # because the debugger doesn't work with @app.tasks

    # send remote task, check if the version is as expected
    task = app.send_task("astro_tasks.tasks.version")
    print(task.get())  # pong my remote app


    # execute my_astro_worker.bat to start a local worker, then run/debug this file
    # this works, all jobs are delivered at once... (then handled 1 by 1)
    #ids = get_jobs_test()

    #handle_job_test("335")
    #task = app.send_task("astro_tasks.tasks.get_jobs")
    #print(task.get())

    # send remote task
    task = app.send_task("astro_tasks.tasks.ping", kwargs=dict(name="nico"))
    print(task.get())  # pong my remote app

    #task = app.send_task("astro_tasks.tasks.handle_job", kwargs=dict(id="624"))
    # print(task.get())

    # run local task - this is the 'ping' for the registration pipeline
    result = registration_test()

    # send remote task - this is the 'ping' for the registration pipeline
    task = app.send_task("astro_tasks.tasks.registration")
    print(task.get())

    print('run has finished')