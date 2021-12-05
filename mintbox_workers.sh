export RABBITMQ_BROKER=amqp://nvermaas:RaBbIt_2019@192.168.178.37:5672
export ASTROBASE_URL=http://192.168.178.37:8008/my_astrobase/
export ASTROBASE_USER=nvermaas
export ASTROBASE_PASSWORD=StErReN_2020
export QUEUE_ASTRO=astro
export POLLING_IN_SECONDS=120
export LOCAL_DATA_DIR=/home/nvermaas/www/data_on_yggdrasil/astrobase/data
celery -A astro_tasks.tasks worker --pool=eventlet -l info --queues astro
