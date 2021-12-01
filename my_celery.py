import os
from os import listdir
from celery import Celery
from celery import current_task

try:
    RABBITMQ_BROKER = os.environ['RABBITMQ_BROKER']
except:
    #RABBITMQ_BROKER = "amqp://celery:celery@192.168.178.37:5672/celery"
    RABBITMQ_BROKER = "amqp://nvermaas:RaBbIt_2019@192.168.178.37:5672"

#
app = Celery('my_celery',
             backend='rpc://',
             broker=RABBITMQ_BROKER)

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)

app.conf.task_routes = {
    'dev_tasks.tasks.*': {'queue': 'dev_q'},
    'astro_tasks.tasks.*': {'queue': 'astro'},
}

#------------------------------------------------------------

@app.task
def ping(name):
    # demo task to see if this can be reached from Django
    return "ponggg " + name + " from " + current_task.request.hostname

@app.task
def dir(my_path):
    return listdir(my_path)