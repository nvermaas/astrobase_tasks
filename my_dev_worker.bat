celery -A dev_tasks.tasks worker --pool=solo -l info -Q dev_q