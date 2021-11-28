from my_tasks import add, ping, dir

def run_examples():
    task = ping.delay('astrobase_tasks')
    print(task.get())

    task = add.delay(4,4)
    print(task.ready())
    print(task.ready())
    print(task.get())
    print(task.ready())

def run_dir():
    task = dir.delay()
    print(task.get())

# client program to test access to celery/broker
if __name__ == '__main__':
    # run_examples()
    run_dir()