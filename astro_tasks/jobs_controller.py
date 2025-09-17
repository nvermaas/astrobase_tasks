import os
from astrobase_io import AstroBaseIO
from . import fits_imaging
from . import tasks

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

astrobaseIO = AstroBaseIO(ASTROBASE_URL, ASTROBASE_USER, ASTROBASE_PASSWORD)

# add with   : http://localhost:8000/my_astrobase/run-command/?command=ping
# check with : http://localhost:8000/my_astrobase/jobs/?job_service=celery
def get_jobs_from_astrobase(job_service):

    try:
        print(f'services.get_jobs_from_astrobase({job_service})')

        query = "status=new&job_service=" + job_service
        # todo: don't just return id's, but also the other parameters in a single request
        ids = astrobaseIO.astrobase_interface.do_GET_LIST(key='jobs:id', query=query)
        astrobaseIO.report("*jobs* : handling " + str(ids), "print")

        # remove jobs
        for id in ids:
            try:
                tasks.handle_job.delay(str(id))
            except Exception as error:
                # something went wrong with this task, continue with the next one
                print(str(error))

    except Exception as error:
        # nothing to do
        print(str(error))
        return

    return ids


# receive the job and handle it based on the 'command' parameter.
def handle_job(id):
    print('services.handle_job('+id+')')
    astrobaseIO.astrobase_interface.do_PUT(key='jobs:status', id=id, taskid=None, value="handling")
    command = astrobaseIO.astrobase_interface.do_GET(key='jobs:command', id=id, taskid=None)
    params = astrobaseIO.astrobase_interface.do_GET(key='jobs:parameters', id=id, taskid=None)
    extra = astrobaseIO.astrobase_interface.do_GET(key='jobs:extra', id=id, taskid=None)

    astrobaseIO.report("*jobs* : executing " + command, "print")
    # execute the command
    try:
        do_execute_command(astrobaseIO, command, params, extra, LOCAL_DATA_DIR)

        astrobaseIO.astrobase_interface.do_PUT(key='jobs:result', id=id, taskid=None, value="ok")
        astrobaseIO.astrobase_interface.do_PUT(key='jobs:status', id=id, taskid=None, value="done")

        # remove job
        astrobaseIO.astrobase_interface.do_DELETE('jobs', id)
        astrobaseIO.report("*jobs* : job " + str(id) + " done", "print")

    except Exception as error:

        print(str(error))
        #astrobaseIO.astrobase_interface.do_PUT(key='jobs:result', id=id, taskid=None, value=str(error))
        #astrobaseIO.astrobase_interface.do_PUT(key='jobs:status', id=id, taskid=None, value="error")
        astrobaseIO.report("*jobs* : job " + str(id) + " - " + str(error), "print")

        # be stern, if a job fails, delete it.
        astrobaseIO.astrobase_interface.do_DELETE('jobs', id)


def create_dataproduct(path_to_grid_file, filename, dp_type):
    print("create_dataproduct(" + filename + ")")
    size = os.path.getsize(path_to_grid_file)
    dp = filename + "#"+dp_type+"#ready#" + str(size)
    return dp


def add_dataproduct(astrobaseIO, taskid, dataproducts_string):
    """
    add dataproduct as a batch to a given observation
    :param atdb:
    :param taskid: taskid of the observation to which the dataproducts are added
    :param dataproducts: a comma separated list of dataproducts containing filename and status per dataproduct
    :param new_status: the status of the new dataproducts, this should be 'defined'.
    :return:
    """
    print("add_dataproduct("+dataproducts_string+")")

    dps = []
    dataproducts = dataproducts_string.split(',')
    for dataproduct in dataproducts:
        dp = {}
        dp['filename'],dp['dataproduct_type'],dp['new_status'],dp['size'] = dataproduct.split('#')
        astrobaseIO.report('adding dataproduct : ' + str(dp['filename']))
        dps.append(dp)

        # check if dataproduct already exist... if so, update
        astrobaseIO.astrobase_interface.do_POST_dataproducts(taskid, dps)


def do_grid(astrobaseIO, params, extra, local_data_dir):
    """
    draw a grid on the image
    """
    list = params.split(',')
    observation_dir = list[0]
    fits_file = list[1]
    input_image_file = list[2]
    output_image_file = list[3]

    try:
        title = list[4].replace('#', ',')
    except:
        title = "Observation"

    try:
        grid_type = list[5]
    except:
        grid_type = "degrees"

    # construct path's based on 'observation_dir:fits_file:image_file'
    # 201023011,4660627.fits,4660627_annotated.jpg

    path_to_fits_file = os.path.join(local_data_dir, os.path.join(observation_dir, fits_file))
    path_to_input_image_file = os.path.join(local_data_dir, os.path.join(observation_dir, input_image_file))
    path_to_output_image_file = os.path.join(local_data_dir, os.path.join(observation_dir, output_image_file))

    path_to_grid_file, ra_min, ra_max, dec_min, dec_max, fov = \
        fits_imaging.draw_grid(path_to_fits_file=path_to_fits_file,
                               path_to_input_image_file=path_to_input_image_file,
                               path_to_output_image_file=path_to_output_image_file,
                               title=title, grid_type=grid_type)

    directory, file = os.path.split(path_to_grid_file)
    if grid_type == 'equatorial':
        dp = create_dataproduct(path_to_grid_file, file, "annotated_grid_eq")
    else:
        dp = create_dataproduct(path_to_grid_file, file, "annotated_grid")

    add_dataproduct(astrobaseIO, observation_dir, dp)
    astrobaseIO.astrobase_interface.do_PUT(key='observations2:ra_min', id=None, taskid=observation_dir,
                                           value=str(ra_min))
    astrobaseIO.astrobase_interface.do_PUT(key='observations2:ra_max', id=None, taskid=observation_dir,
                                           value=str(ra_max))
    astrobaseIO.astrobase_interface.do_PUT(key='observations2:dec_min', id=None, taskid=observation_dir,
                                           value=str(dec_min))
    astrobaseIO.astrobase_interface.do_PUT(key='observations2:dec_max', id=None, taskid=observation_dir,
                                           value=str(dec_max))
    astrobaseIO.astrobase_interface.do_PUT(key='observations2:ra_dec_fov', id=None, taskid=observation_dir, value=fov)


def do_stars(astrobaseIO, params, extra, local_data_dir):
    list = params.split(',')
    observation_dir = list[0]
    astrometry_job = list[1]

    # construct path's based on 'observation_dir:fits_file:image_file'
    # 201023011,4660627.fits,4660627_annotated.jpg

    path_to_fits = os.path.join(local_data_dir, observation_dir)
    path_to_stars_file, max_magnitude = fits_imaging.get_stars(path_to_fits=path_to_fits, astrometry_job=astrometry_job)

    directory, file = os.path.split(path_to_stars_file)
    dp = create_dataproduct(path_to_stars_file, file, "annotated_stars")

    add_dataproduct(astrobaseIO, observation_dir, dp)
    magnitude = astrobaseIO.astrobase_interface.do_GET(key='observations2:magnitude', id=None, taskid=observation_dir)
    if not magnitude:
        astrobaseIO.astrobase_interface.do_PUT(key='observations2:magnitude', id=None, taskid=observation_dir,
                                               value=max_magnitude)


def do_execute_command(astrobaseIO, command, params, extra, local_data_dir):
    print("do_execute_command(" + command + ")")

    if command == "grid":
        do_grid(astrobaseIO,params,extra,local_data_dir)

    if command == "stars":
        do_stars(astrobaseIO,params,extra,local_data_dir)

    # read min/max ra and dec from fits and store in database
    if command == "box":
        # expected parameters:
        # params = [taskid,path_to_fits]

        list = params.split(',')
        taskid = list[0]
        fits_file = list[1]
        path_to_fits_file = os.path.join(local_data_dir, os.path.join(taskid, fits_file))

        box = fits_imaging.get_box(path_to_fits_file)
        astrobaseIO.astrobase_interface.do_PUT(key='observations2:box', id=None, taskid=taskid, value=box)

    if command == "draw_extra":
        list = params.split(',')
        observation_dir = list[0]
        fits_file = list[1]
        input_image_file = list[2]
        output_image_file = list[3]

         # construct path's based on 'observation_dir:fits_file:image_file'
        # 201023011,4660627.fits,4660627_annotated.jpg

        path_to_fits_file = os.path.join(local_data_dir,os.path.join(observation_dir, fits_file))
        path_to_input_image_file = os.path.join(local_data_dir,os.path.join(observation_dir, input_image_file))
        path_to_output_image_file = os.path.join(local_data_dir,os.path.join(observation_dir, output_image_file))

        # draw on image file
        fits_imaging.draw_extra(path_to_fits_file=path_to_fits_file,
                        path_to_input_image_file=path_to_input_image_file,
                        path_to_output_image_file=path_to_output_image_file,
                        extra=extra)


    if command == "transient":
        list = params.split(',')
        observation_dir = list[0]
        fits_file = list[1]
        input_image_file = list[2]
        output_image_file = list[3]

         # construct path's based on 'observation_dir:fits_file:image_file'
        # 201023011,4660627.fits,4660627_annotated.jpg

        path_to_fits_file = os.path.join(local_data_dir,os.path.join(observation_dir, fits_file))
        path_to_input_image_file = os.path.join(local_data_dir,os.path.join(observation_dir, input_image_file))
        path_to_output_image_file = os.path.join(local_data_dir,os.path.join(observation_dir, output_image_file))

        # draw on image file
        path_to_new_file = fits_imaging.draw_extra(path_to_fits_file=path_to_fits_file,
                        path_to_input_image_file=path_to_input_image_file,
                        path_to_output_image_file=path_to_output_image_file,
                        extra=extra)

        directory, file = os.path.split(path_to_new_file)
        dp = create_dataproduct(path_to_new_file,file, "annotated_transient")

        add_dataproduct(astrobaseIO, observation_dir, dp)


    if command == "exoplanets":
        list = params.split(',')
        observation_dir = list[0]
        fits_file = list[1]
        input_image_file = list[2]
        output_image_file = list[3]

         # construct path's based on 'observation_dir:fits_file:image_file'
        # 201023011,4660627.fits,4660627_annotated.jpg

        path_to_fits_file = os.path.join(local_data_dir,os.path.join(observation_dir, fits_file))
        path_to_input_image_file = os.path.join(local_data_dir,os.path.join(observation_dir, input_image_file))
        path_to_output_image_file = os.path.join(local_data_dir,os.path.join(observation_dir, output_image_file))

        # draw on image file
        path_to_new_file = fits_imaging.draw_extra(path_to_fits_file=path_to_fits_file,
                        path_to_input_image_file=path_to_input_image_file,
                        path_to_output_image_file=path_to_output_image_file,
                        extra=extra)

        directory, file = os.path.split(path_to_new_file)
        dp = create_dataproduct(path_to_new_file,file, "annotated_exoplanets")

        add_dataproduct(astrobaseIO, observation_dir, dp)


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
            path_to_new_file = fits_imaging.image_cutout(
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

            raise error

