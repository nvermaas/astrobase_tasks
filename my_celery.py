import os
from celery import Celery

try:
    RABBITMQ_BROKER = os.environ['RABBITMQ_BROKER']
except:
    RABBITMQ_BROKER = "amqp://nvermaas:RaBbIt_2019@192.168.178.37:5672"

# switch to dev mode in QUEUE_ASTRO is not set
try:
    QUEUE_ASTRO = os.environ['QUEUE_ASTRO']
except:
    QUEUE_ASTRO = 'dev_q'
    #QUEUE_ASTRO = 'astro'

try:
    POLLING_IN_SECONDS = float(os.environ['POLLING_IN_SECONDS'])
except:
    POLLING_IN_SECONDS = 30


app = Celery('my_celery',
             backend='rpc://',
             broker=RABBITMQ_BROKER,
             include=['astro_tasks.tasks','dev_tasks.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=60,
)

# all astro_tasks go to the queue 'astro'.
# there is only 1 remote worker started, for 'astro_tasks.task'.
# for development, locally start the dev worker with 'my_dev_worker.bat'
app.conf.task_routes = {
    #'astro_tasks.tasks.*': {'queue': QUEUE_ASTRO},
    'astro_tasks.tasks.*': {'queue': 'astro'},
    'dev_tasks.tasks.*': {'queue': 'dev_q'},
}

app.conf.beat_schedule = {
  'refresh': {
    'task': 'astro_tasks.tasks.get_jobs',
    'schedule': POLLING_IN_SECONDS,
}}

app.autodiscover_tasks(force=True)