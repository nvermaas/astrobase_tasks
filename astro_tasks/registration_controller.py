import os
from astrobase_io import AstroBaseIO
from . import tasks
from .service_ingest import do_ingest
from .service_submit import do_submit
from .service_cleanup import do_cleanup
from .service_processor import do_processor

try:
    # production mode
    ASTROBASE_URL = os.environ['ASTROBASE_URL']
    ASTROBASE_USER = os.environ['ASTROBASE_USER']
    ASTROBASE_PASSWORD = os.environ['ASTROBASE_PASSWORD']
    LOCAL_DATA_DIR = os.environ['LOCAL_DATA_DIR']
    LANDING_PAD = os.environ['LANDING_PAD']
    ASTROMETRY_URL = os.environ['ASTROMETRY_URL']
    ASTROMETRY_API_KEY = os.environ['ASTROMETRY_API_KEY']

except:
    # development mode
    ASTROBASE_URL = "http://localhost:8000/my_astrobase/"
    LOCAL_DATA_DIR = 'd:\my_astrobase\data'
    LANDING_PAD = 'd:\my_astrobase\landing_pad'
    ASTROMETRY_URL = "http://nova.astrometry.net"

astrobaseIO = AstroBaseIO(ASTROBASE_URL, ASTROBASE_USER, ASTROBASE_PASSWORD)

# this is a 'ping' to the registration pipeline
# this will run all the registration services once.
def run_registration_pipeline():
    print('registration_controller.run_registration_pipeline()')

    # execute all the services (async)
    tasks.run_ingest.delay()
    tasks.run_submit.delay()
    tasks.run_processor.delay()
    tasks.run_cleanup.delay()

    # execute ingest service
    # do_ingest(astrobaseIO, LANDING_PAD, LOCAL_DATA_DIR)
    print('done run_registration_pipeline')


def run_ingest():
    print('registration_controller.ingest()')

    # execute ingest service
    do_ingest(astrobaseIO, LANDING_PAD, LOCAL_DATA_DIR)
    print('done ingest')


def run_submit():
    print('registration_controller.ingest()')

    do_submit(astrobaseIO, LOCAL_DATA_DIR, ASTROMETRY_URL, ASTROMETRY_API_KEY)
    print('done submit')


def run_processor():
    print('registration_controller.processor()')

    do_processor(astrobaseIO, LOCAL_DATA_DIR, ASTROMETRY_URL, ASTROMETRY_API_KEY)
    print('done processor')


def run_cleanup():
    print('registration_controller.run_cleanup()')

    # execute ingest service
    do_cleanup(astrobaseIO, LOCAL_DATA_DIR)
    print('done cleanup')