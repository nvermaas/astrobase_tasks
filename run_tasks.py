from my_tasks import app, add, ping, dir
from dev_tasks.tasks import dev_ping

def run_examples():
    task = ping.delay('astrobase_tasks')
    print(task.get())

    task = add.delay(4,4)
    print(task.ready())
    print(task.ready())
    print(task.get())
    print(task.ready())

def run_ping(name):
    task = ping.delay(name)
    print(task.get())

def run_dev_ping(name):
    task = dev_ping.delay(name)
    print(task.get())

def run_dir(my_path):
    task = dir.delay(my_path)
    return task.get()


# client program to test access to celery/broker
if __name__ == '__main__':
    # run_examples()

    # ping on default queue
    run_ping('Nico')

    # ping on queue 'dev'
    run_dev_ping('Nico')

    dir = run_dir(".")
    print(dir)
