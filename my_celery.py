import os
from celery import Celery
import astro_tasks, dev_tasks

VERSION = "16 jul 2023"

try:
    RABBITMQ_BROKER = os.environ['RABBITMQ_BROKER']
except:
    print("ERROR: define the RABBITMQ_BROKER environment variable" )

try:
    POLLING_IN_SECONDS = float(os.environ['POLLING_IN_SECONDS'])
except:
    POLLING_IN_SECONDS = 30


app = Celery('my_celery',
             backend='rpc://',
             broker=RABBITMQ_BROKER)

app.autodiscover_tasks(['astro_tasks','dev_tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=60,
)

# all astro_tasks go to the queue 'astro'.
# there is only 1 remote worker started, for 'astro_tasks.task'.
# for development, locally start the dev worker with 'my_dev_worker.bat'
app.conf.task_routes = {
    'astro_tasks.tasks.*': {'queue': 'astro'},
    'astro_tasks.tasks.handle_cutout': {'queue': 'cutout'},
    'astro_tasks.tasks.run_registration_pipeline': {'queue': 'registration'},
    'astro_tasks.tasks.run_ingest': {'queue': 'registration'},
    'astro_tasks.tasks.run_submit': {'queue': 'registration'},
    'astro_tasks.tasks.run_processor': {'queue': 'registration'},
    'astro_tasks.tasks.run_cleanup': {'queue': 'registration'},
    'dev_tasks.tasks.*': {'queue': 'dev_q'},
}

app.conf.beat_schedule = {
  'refresh': {
    'task': 'astro_tasks.tasks.run_registration_pipeline',
    'schedule': POLLING_IN_SECONDS,
}}

