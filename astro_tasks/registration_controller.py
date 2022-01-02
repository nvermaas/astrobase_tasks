import os
from astrobase_io import AstroBaseIO
from . import tasks
from .registration_services import submit

try:
    # production mode
    ASTROBASE_URL = os.environ['ASTROBASE_URL']
    ASTROBASE_USER = os.environ['ASTROBASE_USER']
    ASTROBASE_PASSWORD = os.environ['ASTROBASE_PASSWORD']
    LOCAL_DATA_DIR = os.environ['LOCAL_DATA_DIR']
    LANDING_PAD = os.environ['LANDING_PAD']
except:
    # development mode
    ASTROBASE_URL = "http://localhost:8000/my_astrobase/"
    ASTROBASE_USER = "dev_client"
    ASTROBASE_PASSWORD = "my_dev_client_2021"
    LOCAL_DATA_DIR = 'd:\my_astrobase\data'
    LANDING_PAD = 'd:\my_astrobase\landing_pad'


def handle_registration():
    print('registration_controller.handle_registration()')

    # execute submit service
    submit(LANDING_PAD)