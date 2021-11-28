from .worker import app

@app.task
def add(x, y):
    for i in range(1000):
        print(i)
    return x + y + i

@app.task
def ping(name):
    # demo task to see if this can be reached from Django
    return "pong " + name