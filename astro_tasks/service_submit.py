"""
    File name: submit.py
    Author: Nico Vermaas
    Date created: 2019-10-23
    Description: - submit job to astrometry.net
"""

import os
import platform
from datetime import datetime
import requests,json
import urllib.request

from astrobase_services.astrometry_client import Client

def get_creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getmtime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime


def get_job_id(submission_id, astrometry_url, astrometry_api_key):

    client = Client(apiurl=astrometry_url+"/api/")
    client.login(apikey=astrometry_api_key)
    submission_result = client.sub_status(submission_id, justdict=True)
    print("submission_result :" + str(submission_result))

    try:
        job_id = str(submission_result['jobs'][0])
        return job_id
    except:
        return None


def check_submission_status(astrobaseIO, submission_id, astrometry_url, astrometry_api_key):
    """
    check of the pipeline at astrometry is done processing the submitted image
    :param submission_id:
    :return:
    """
    # astrobaseIO.report("-- check_submission_status("+ submission_id + ")", "print")

    try:
        job_id = get_job_id(submission_id, astrometry_url, astrometry_api_key)
        job_results = get_job_results(astrobaseIO, job_id, astrometry_url, astrometry_api_key, False)
        print("job_results: " + str(job_results))
        if job_results['job']['status']=='success':
            radius = job_results['calibration']['radius']
            return 'success',radius
        if job_results['job']['status']=='failure':
            return 'failure',0
    except:
        return 'unfinished',0
    return "unknown"

def get_job_results(astrobaseIO, job_id, astrometry_url, astrometry_api_key, justdict):
    """
    {'objects_in_field':
        ['The star 61Leo', 'The star υ2Hya', 'The star φLeo', 'The star υ1Hya',
         'The star γCrt', 'The star Alkes (αCrt)', 'The star μHya', 'The star λHya',
         'The star δCrt', 'The star νHya', 'Part of the constellation Hydra (Hya)',
         'Part of the constellation Crater (Crt)'],
     'machine_tags':
        ['The star 61Leo', 'The star υ2Hya', 'The star φLeo', 'The star υ1Hya', 'The star γCrt',
         'The star Alkes (αCrt)', 'The star μHya', 'The star λHya', 'The star δCrt', 'The star νHya',
         'Part of the constellation Hydra (Hya)', 'Part of the constellation Crater (Crt)'],
     'status': 'success',
     'tags':
        ['The star 61Leo', 'The star υ2Hya', 'The star φLeo', 'The star υ1Hya',
         'The star γCrt', 'The star Alkes (αCrt)', 'The star μHya', 'The star λHya',
         'The star δCrt', 'The star νHya', 'Part of the constellation Hydra (Hya)',
         'Part of the constellation Crater (Crt)'],
     'calibration':
            {'orientation': 180.47305689878488,
            'dec': -11.294944542800003,
            'pixscale': 541.8204596987174,
            'radius': 20.721878048048463,
            'parity': 1.0,
            'ra': 166.270006359},
            'original_filename': 'SouthPoleTransformed/1565.png'
            }

    :param job_id:
    :return:
    """
    # astrobaseIO.report("---- get_job_results(" + str(job_id) + ")", "print")
    # login to astrometry with the API_KEY
    client = Client(apiurl=astrometry_url+"/api/")
    client.login(apikey=astrometry_api_key)

    result = client.job_status(job_id, justdict=justdict)
    return result


def get_submission(astrobaseIO, submission_id, astrometry_url, astrometry_api_key):
    """
    check of the pipeline at astrometry is done processing the submitted image
    :param submission_id:
    :return:
    """
    # login to astrometry with the API_KEY
    astrobaseIO.report("---- get_submission(" + submission_id + ")", "print")

    client = Client(apiurl=astrometry_url+"/api/")
    client.login(apikey=astrometry_api_key)

    result = client.sub_status(submission_id, justdict=True)
    return result

#-------------------------------------------------------------------------------------
def do_submit_jobs(astrobaseIO, local_data_dir, astrometry_url, astrometry_api_key):

    ASTROMETRY_URL = astrometry_url
    ASTROMETRY_API_KEY = astrometry_api_key

    def submit_job_to_astrometry(path_to_file):
        """
        http://astrometry.net/doc/net/api.html
        :param path_to_file:
        :return:
        """
        astrobaseIO.report("-- submit_job_to_astrometry at " + ASTROMETRY_URL + ")", "print")
        # login to astrometry with the API_KEY
        client = Client(apiurl=ASTROMETRY_URL+"/api/")
        client.login(apikey=ASTROMETRY_API_KEY)

        result = client.upload(fn=path_to_file)

        print(result)
        job = result['subid']
        job_status = result['status']
        return job, job_status

    # --- start of function body ---

    STATUS_START = "pending"
    STATUS_END = "submitted"

    taskIDs = astrobaseIO.astrobase_interface.do_GET_LIST(key='observations2:taskID', query='my_status=' + STATUS_START)
    if len(taskIDs) > 0:
        astrobaseIO.report("-- do_submit_jobs()", "print")

        # loop through the 'processing' observations
        for taskID in taskIDs:

            astrobaseIO.astrobase_interface.do_PUT(key='observations2:new_status', id=None, taskid=taskID, value="submitting")

            # find the raw dataproducts
            derived_raw_image = astrobaseIO.astrobase_interface.do_GET(key='observations2:derived_raw_image', id=None, taskid=taskID)
            dirname, filename = os.path.split(derived_raw_image)

            directory = os.path.join(local_data_dir,taskID)
            path_to_file = os.path.join(directory,filename)

            astrobaseIO.report("*processor* : processing " + filename, "slack")

            # do the magic!
            # when using files
            submission_id, submission_status = submit_job_to_astrometry(path_to_file)

            # when using urls
            #submission_id, submission_status = submit_job_to_astrometry(filename)

            if submission_status=="success":
                # write the current job to the observation.
                # job_url = ASTROMETRY_URL + "/status/"+submission_id
                astrobaseIO.astrobase_interface.do_PUT(key='observations2:job', id=None, taskid=taskID, value=submission_id)
                astrobaseIO.astrobase_interface.do_PUT(key='observations2:astrometry_url', id=None, taskid=taskID, value=ASTROMETRY_URL)

                # when all raw dps have been processed, put observation to 'processed'.
                astrobaseIO.astrobase_interface.do_PUT(key='observations2:new_status', id=None, taskid=taskID, value="submitted")
                astrobaseIO.report("*processor* : submitted job " + str(submission_id) + " for " + taskID + " " + STATUS_END,"slack")
            else:
                astrobaseIO.astrobase_interface.do_PUT(key='observations2:new_status', id=None, taskid=taskID, value="failed submitting")
                astrobaseIO.report("*processor* : submitted job " + str(submission_id) + " for " + taskID + " failed.","slack")

#-------------------------------------------------------------------------------------
def do_check_submission_status(astrobaseIO, astrometry_url, astrometry_api_key):

    ASTROMETRY_URL = astrometry_url
    ASTROMETRY_API_KEY = astrometry_api_key


    # --- start of function body ---

    STATUS_START = "submitted"
    query = 'my_status__in='+STATUS_START
    taskIDs = astrobaseIO.astrobase_interface.do_GET_LIST(key='observations2:taskID', query=query)
    if len(taskIDs) > 0:
        astrobaseIO.report("-- do_check_submission_status()", "print")

        # loop through the 'submitted' and check for the success status
        for taskID in taskIDs:
            # astrobaseIO.astrobase_interface.do_PUT(key='observations:new_status', id=None, taskid=taskID, value="processing")

            # get the astrometry submission_id to check
            submission_id = astrobaseIO.astrobase_interface.do_GET(key='observations2:job', id=None, taskid=taskID)
            job_status, radius = check_submission_status(astrobaseIO,submission_id, astrometry_url, astrometry_api_key)
            astrobaseIO.report("*processor* : status of job " + submission_id + " = " + job_status, "print")

            if job_status == 'success':
                astrobaseIO.astrobase_interface.do_PUT(key='observations2:new_status', id=None,taskid=taskID,value="processed")
                astrobaseIO.astrobase_interface.do_PUT(key='observations2:field_fov', id=None, taskid=taskID, value=radius)
            if job_status == 'failure':
                astrobaseIO.astrobase_interface.do_PUT(key='observations2:new_status', id=None,taskid=taskID,value="failed")


# --- Main Service -----------------------------------------------------------------------------------------------

def do_submit(astrobaseIO, local_data_dir, astrometry_url, astrometry_api_key):
    #astrobaseIO.report("- do_submit()", "print")

    # submit new jobs to astrometry.net
    do_submit_jobs(astrobaseIO, local_data_dir, astrometry_url, astrometry_api_key)

    # check if the job is ready and handle results on success.
    do_check_submission_status(astrobaseIO, astrometry_url, astrometry_api_key)

