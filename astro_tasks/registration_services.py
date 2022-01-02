import os

def submit(landing_pad):
    print('registration_services.submit()')
    print('landing_pad =  '+landing_pad)

    for dirpath, dirnames, filenames in os.walk(landing_pad, followlinks=True):

        for filename in filenames:
            path_to_file = os.path.join(dirpath, filename)
            name, ext = filename.split(".")
            print("*ingest* : add observation " + path_to_file)
