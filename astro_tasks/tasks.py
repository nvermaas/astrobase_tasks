import os
from celery import current_task
from my_tasks import app

try:
    ASTROBASE_URL = os.environ['ASTROBASE_URL']
except:
    ASTROBASE_URL = "http://localhost:8000/my_astrobase/"

@app.task
def get_jobs():
    # look for pending jobs in astrobase
    return "get_jobs() from " + current_task.request.hostname


# test the tasks
if __name__ == '__main__':
    task = get_jobs.delay()
    try:
        results = task.get(timeout=1)
    except:
        results = str("Timeout for get_jobs: is there a worker running for this queue?")
    print(results)
