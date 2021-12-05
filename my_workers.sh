#celery -A astro_tasks.tasks worker --pool=solo -l info -Q astro
celery -A astro_tasks.tasks worker --pool=eventlet -l info --queues astro