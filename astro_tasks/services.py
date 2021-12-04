import os
from astrobase_io import AstroBaseIO
from . import fits

try:
    # production mode
    ASTROBASE_URL = os.environ['ASTROBASE_URL']
    ASTROBASE_USER = os.environ['ASTROBASE_USER']
    ASTROBASE_PASSWORD = os.environ['ASTROBASE_PASSWORD']
    LOCAL_DATA_DIR = os.environ['LOCAL_DATA_DIR']
except:
    # development mode
    ASTROBASE_URL = "http://localhost:8000/my_astrobase/"
    ASTROBASE_USER = "dev_client"
    ASTROBASE_PASSWORD = "my_dev_client_2021"
    LOCAL_DATA_DIR = 'd:\my_astrobase\data'


# add with   : http://localhost:8000/my_astrobase/run-command/?command=ping
# check with : http://localhost:8000/my_astrobase/jobs/?queue=astro
def get_jobs_from_astrobase(jobs_queue):
    astrobaseIO = AstroBaseIO(ASTROBASE_URL, ASTROBASE_USER, ASTROBASE_PASSWORD)
    try:
        query = "status=new&queue=" + jobs_queue
        # todo: don't just return id's, but also the other parameters in a single request
        ids = astrobaseIO.astrobase_interface.do_GET_LIST(key='jobs:id', query=query)

        # remove jobs
        for id in ids:
            handle_job(astrobaseIO,id)

    except:
        # nothing to do
        return
    result = ids
    return result


# receive the job and handle it based on the 'command' parameter.
def handle_job(astrobaseIO,id):

    astrobaseIO.astrobase_interface.do_PUT(key='jobs:status', id=id, taskid=None, value="handling")
    command = astrobaseIO.astrobase_interface.do_GET(key='jobs:command', id=id, taskid=None)
    params = astrobaseIO.astrobase_interface.do_GET(key='jobs:parameters', id=id, taskid=None)
    extra = astrobaseIO.astrobase_interface.do_GET(key='jobs:extra', id=id, taskid=None)

    astrobaseIO.report("*jobs* : executing " + command, "slack")
    # execute the command
    try:
        do_execute_command(astrobaseIO, command, params, extra, LOCAL_DATA_DIR)

        astrobaseIO.astrobase_interface.do_PUT(key='jobs:result', id=id, taskid=None, value="ok")
        astrobaseIO.astrobase_interface.do_PUT(key='jobs:status', id=id, taskid=None, value="done")

        # remove job
        astrobaseIO.astrobase_interface.do_DELETE('jobs', id)
        astrobaseIO.report("*jobs* : job " + str(id) + " done", "slack")

    except Exception as error:

        print(str(error))
        #astrobaseIO.astrobase_interface.do_PUT(key='jobs:result', id=id, taskid=None, value=str(error))
        #astrobaseIO.astrobase_interface.do_PUT(key='jobs:status', id=id, taskid=None, value="error")
        astrobaseIO.report("*jobs* : job " + str(id) + " - " + str(error), "slack")

        # be stern, if a job fails, delete it.
        astrobaseIO.astrobase_interface.do_DELETE('jobs', id)


def do_execute_command(astrobaseIO, command, params, extra, local_data_dir):
    print("do_execute_command(" + command + ")")

    if command == "image_cutout":
        list = params.split(',')
        observation_dir = list[0]
        fits_file = list[1]
        input_image_file = list[2]
        output_image_file = list[3]
        directory,filename = output_image_file.split(os.path.sep)

        # construct path's based on 'observation_dir:fits_file:image_file'
        # 201023011,4660627.fits,4660627_annotated.jpg

        path_to_fits_file = os.path.join(local_data_dir,os.path.join(observation_dir, fits_file))
        path_to_input_image_file = os.path.join(local_data_dir,os.path.join(observation_dir, input_image_file))
        path_to_output_image_file = os.path.join(local_data_dir,os.path.join("cutouts", output_image_file))

        # draw on image file
        try:
            path_to_new_file = fits.image_cutout(
                path_to_fits_file=path_to_fits_file,
                path_to_input_image_file=path_to_input_image_file,
                path_to_output_image_file=path_to_output_image_file,
                extra=extra)

            path, file = os.path.split(path_to_new_file)

            # report the results to astrobase
            astrobaseIO.astrobase_interface.do_PUT(key='cutouts:visible', id=filename, value="true")
            astrobaseIO.astrobase_interface.do_PUT(key='cutouts:status', id=filename, value="job_done")

        except Exception as error:
            astrobaseIO.astrobase_interface.do_PUT(key='cutouts:visible', id=filename, value="false")
            astrobaseIO.astrobase_interface.do_PUT(key='cutouts:status', id=filename, value="job_failed")

            # remove the attempted cutouts that failed from the database
            # astrobaseIO.astrobase_interface.do_DELETE(resource='cutouts', id=filename)

            # throw the exception again to be handled upstream
            raise error
