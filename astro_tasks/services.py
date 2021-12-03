from astrobase_io import AstroBaseIO

try:
    ASTROBASE_URL = os.environ['ASTROBASE_URL']
    ASTROBASE_USER = os.environ['ASTROBASE_USER']
    ASTROBASE_PASSWORD = os.environ['ASTROBASE_PASSWORD']
except:
    ASTROBASE_URL = "http://localhost:8000/my_astrobase/"
    ASTROBASE_USER = "dev_client"
    ASTROBASE_PASSWORD = "my_dev_client_2021"


# add with   : http://localhost:8000/my_astrobase/run-command/?command=ping
# check with : http://localhost:8000/my_astrobase/jobs/?queue=astro
def get_jobs_from_astrobase(jobs_queue):
    astrobaseIO = AstroBaseIO(ASTROBASE_URL, ASTROBASE_USER, ASTROBASE_PASSWORD)
    try:
        query = "status=new&queue=" + jobs_queue
        ids = astrobaseIO.astrobase_interface.do_GET_LIST(key='jobs:id', query=query)

        # remove jobs
        for id in ids:
            print('delete job '+str(id))
            astrobaseIO.astrobase_interface.do_DELETE('jobs', id)

    except:
        # nothing to do
        return
    result = ids
    return result
