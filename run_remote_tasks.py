from my_tasks import app

def run_examples():
    task = app.send_task("my_tasks.ping", kwargs=dict(name="my remote app"))
    print(task.get())  # pong my remote app

# client program to test access to celery/broker
if __name__ == '__main__':
    run_examples()