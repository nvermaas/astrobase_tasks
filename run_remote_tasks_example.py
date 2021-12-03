from my_celery import app

def remote_ping():
    task = app.send_task("astro_tasks.tasks.ping", kwargs=dict(name="my remote app"))
    print(task.get())  # pong my remote app

def remote_dir(my_path):
    task = app.send_task("astro_tasks.tasks.dir", kwargs=dict(my_path=my_path))
    return(task.get())  # pong my remote app

def remote_get_jobs():
    task = app.send_task("astro_tasks.tasks.get_jobs")
    return(task.get())  # pong my remote app

# client program to test access to celery/broker
if __name__ == '__main__':
    remote_ping()
    #print(remote_dir("/data"))
    # The astrobase data directory on the NAS is mounted as '/data' by the docker-compose.yml file
    # /home/nvermaas/www/data_on_yggdrasil/astrobase/data:/data
    print(remote_get_jobs())
