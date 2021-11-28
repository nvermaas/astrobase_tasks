from my_tasks import app

def run_ping():
    task = app.send_task("my_tasks.ping", kwargs=dict(name="my remote app"))
    print(task.get())  # pong my remote app

def run_dir(my_path):
    task = app.send_task("my_tasks.dir", kwargs=dict(my_path=my_path))
    return(task.get())  # pong my remote app

# client program to test access to celery/broker
if __name__ == '__main__':
    run_ping()
    print(run_dir("/shared"))
    #print(run_dir("/data"))