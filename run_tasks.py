from my_tasks.tasks import add, ping

def run_examples():
    task = ping.delay('astrobase_tasks')
    print(task.get())

    task = add.delay(4,4)
    print(task.ready())

    print(task.get())
    print(task.ready())

if __name__ == '__main__':
    run_examples()