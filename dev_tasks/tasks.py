from os import listdir
from celery import current_task
from my_tasks import app

@app.task
def dev_ping(name):
    # demo task to see if this can be reached from Django
    return "dev_ponggg " + name + " from " + current_task.request.hostname

@app.task
def dev_dir(my_path):
    return listdir(my_path)