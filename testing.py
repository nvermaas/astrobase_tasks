
from astro_tasks.tasks import get_jobs

def run_get_jobs():
    task = get_jobs.delay()
    try:
        results = task.get(timeout=1)
    except:
        results = str("Timeout for get_jobs: is there a worker running for this queue?")
    return results

# client program to test access to celery/broker
if __name__ == '__main__':

    my_jobs = run_get_jobs()
    print("jobs: " + str(my_jobs))