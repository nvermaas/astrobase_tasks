
from dev_tasks.tasks import dev_ping, dev_dir
from astro_tasks.tasks import ping, dir, get_jobs

def run_dev_ping(name):
    task = dev_ping.delay(name)
    try:
        results = task.get(timeout=1)
    except:
        results = str("Timeout for dev_ping: is there a worker running for this queue?")
    print(results)

def run_ping(name):
    task = ping.delay(name)
    try:
        results = task.get(timeout=1)
    except:
        results = str("Timeout for ping: is there a worker running for this queue?")
    print(results)

def run_dev_dir(my_path):
    task = dev_dir.delay(my_path)
    try:
        results = task.get(timeout=1)
    except:
        results = str("Timeout for dev_dir: is there a worker running for this queue?")
    return results

def run_dir(my_path):
    task = dir.delay(my_path)
    try:
        results = task.get(timeout=5)
    except:
        results = str("Timeout for dir: is there a worker running for this queue?")
    return results

def run_get_jobs():
    task = get_jobs.delay()
    try:
        results = task.get(timeout=5)
    except:
        results = str("Timeout for get_jobs: is there a worker running for this queue?")
    return results

# client program to test access to celery/broker
if __name__ == '__main__':

    # ping on queue 'dev_q'
    # executed by 'my_dev_worker.bat':
    # celery -A dev_tasks.tasks worker --pool=solo -l info -Q dev_q
    run_dev_ping('Nico') # dev_ponggg Nico from celery@NBVERMAAS-W10

    # ping on default queue 'celery'
    # executed by 'worker.bat':
    # celery -A my_tasks worker --pool=solo -l info
    # or by worker on mintbox by the docker-compose.yml file:
    # celery -A my_tasks worker --pool=eventlet -l info --concurrency=20 -Q celery,mintbox
    run_ping('Nico') # ponggg Nico from celery@c20e8af23634

    my_dir = run_dev_dir(".")
    print("dev_dir: "+str(my_dir))

    # prove that the remove '/data' directory can be accessed
    my_dir = run_dir("/data")
    print("prod_dir: "+str(my_dir)) # ['090313004', '211122003', '210228002', '210222003', '200819007', '191120006', '200329002

    my_jobs = run_get_jobs()
    print("get_jobs: " + str(my_jobs))