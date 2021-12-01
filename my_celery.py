import os
from celery import Celery

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

# all astro_tasks go to the queue 'astro'.
# there is only 1 remote worker started, for 'astro_tasks.task'.
# for development, locally start the dev worker with 'my_dev_worker.bat'
app.conf.task_routes = {
    'dev_tasks.tasks.*': {'queue': 'dev_q'},
    'astro_tasks.tasks.*': {'queue': 'astro'},
}
