from astrobase_io import AstroBaseIO

try:
    ASTROBASE_URL = os.environ['ASTROBASE_URL']
    ASTROBASE_USER = os.environ['ASTROBASE_USER']
    ASTROBASE_PASSWORD = os.environ['ASTROBASE_PASSWORD']
except:
    ASTROBASE_URL = "http://localhost:8000/my_astrobase/"
    ASTROBASE_USER = "nvermaas"
    ASTROBASE_PASSWORD = "StErReN_2020"


def get_number_of_jobs(queue):
    astrobaseIO = AstroBaseIO(ASTROBASE_URL, ASTROBASE_USER, ASTROBASE_PASSWORD)
    try:
        query = "status=new&queue=" + queue
        ids = astrobaseIO.astrobase_interface.do_GET_LIST(key='jobs:id', query=query)
    except:
        # nothing to do
        return
    result = ids
    return result
