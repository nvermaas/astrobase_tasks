import os
from celery import Celery

#RABBITMQ_BROKER = "amqp://celery:celery@192.168.178.37:5672/celery"
RABBITMQ_BROKER = os.environ['RABBITMQ_BROKER']

app = Celery('my_tasks',
             backend='rpc://',
             broker=RABBITMQ_BROKER)

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)

@app.task
def add(x, y):
    for i in range(1000):
        print(i)
    return x + y + i

@app.task
def ping(name):
    # demo task to see if this can be reached from Django
    return "pong " + name



