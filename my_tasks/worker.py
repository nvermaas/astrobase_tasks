from celery import Celery

RABBITMQ_BROKER = "amqp://celery:celery@192.168.178.37:5672/celery"
app = Celery('tasks',
             backend='rpc://',
             broker=RABBITMQ_BROKER,
             include=['my_tasks.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)

if __name__ == '__main__':
    app.start()