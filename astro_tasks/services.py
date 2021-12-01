
try:
    ASTROBASE_URL = os.environ['ASTROBASE_URL']
except:
    ASTROBASE_URL = "http://localhost:8000/my_astrobase/"

def get_number_of_jobs():
    url = ASTROBASE_URL + 'jobs'
    print(url)
    return 1
