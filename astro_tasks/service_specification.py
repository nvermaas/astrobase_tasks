"""
    File name: service_specification.py
    Author: Nico Vermaas
    Date created: 2019-10-13
     Description: (Manual) specification service to add Observation and dataproducts
"""

import os
import datetime
import time
import json
import logging

TASKID_TIME_FORMAT = "%Y%m%d"
DURATION_TIME_FORMAT ="%H:%M:%S"
SPECIFICATION_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# --- Helper Functions ---------------------------------------------------------------------------------------------

# decorator to time the execution of a function
def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('execution time: %r  %2.2f ms' % \
                  (method.__name__, (te - ts) * 1000))
        return result
    return timed


def generate_taskid(astrobase, timestamp, taskid_postfix):
    """
    :param astrobase: the atdb interface abstraction layer
    :param timestamp: timestamp on which the taskid is based
    :param taskid_postfix: optional addition to the tasked, like 190405001_IMG
    :return: taskid
    """

    taskid = astrobase.astrobase_interface.do_GET_NextTaskID(timestamp, taskid_postfix)
    return taskid


# add dataproducts as a batch

def add_dataproducts(astrobase, taskid, dataproducts_string):
    """
    add dataproduct as a batch to a given observation
    :param atdb:
    :param taskid: taskid of the observation to which the dataproducts are added
    :param dataproducts: a comma separated list of dataproducts containing filename and status per dataproduct
    :param new_status: the status of the new dataproducts, this should be 'defined'.
    :return:
    """
    dps = []
    dataproducts = dataproducts_string.split(',')
    for dataproduct in dataproducts:
        dp = {}
        dp['filename'],dp['dataproduct_type'],dp['new_status'],dp['size'] = dataproduct.split(':')
        astrobase.report('adding dataproduct : ' + str(dp['filename']))
        dps.append(dp)

    if len(dps)>0:
        astrobase.astrobase_interface.do_POST_dataproducts(taskid, dps)
    else:
        astrobase.report("*specification* : (intentionally?) no dataproducts created")



# --- Main Service -------
# ----------------------------------------------------------------------------------------

def do_specification(astrobase, taskid, initial_status, field_name, description, date,
                     field_ra=0.0, field_dec=0.0, field_fov=0.0,
                     observing_mode="raw", process_type="observation", dataproducts="",
                     data_location="", name=""):

    # if no taskid is given, then generate the new taskid based on date and (optional) taskid_postfix
    STATUS_OBS_END = 'raw'  # this service will leave the observation in this state

    if initial_status!=None:
        STATUS_OBS_END = initial_status  # this service will leave the observation in this state

    if taskid is None:
        if date!=None:
            target_time = datetime.datetime.strptime(date, SPECIFICATION_TIME_FORMAT)
            timestamp = target_time.strftime(TASKID_TIME_FORMAT)
        else:
            timestamp = datetime.datetime.now().strftime(TASKID_TIME_FORMAT)
        taskid = generate_taskid(astrobase, timestamp)


    # --- construct payload as json ----------------
    payload = "{"
    payload += '"name" : "' + str(name) + '",'
    payload += '"description" : "' + str(description) + '",'
    payload += '"taskID" : "' + str(taskid) + '",'
    payload += '"date" : "' + str(date) + '",'
    payload += '"task_type" : "observation",'
    payload += '"field_name" : "' + str(field_name) + '",'
    payload += '"field_ra" : "' + str(field_ra) + '",'
    payload += '"field_dec" : "' + str(field_dec) + '",'
    payload += '"field_fov" : "' + str(field_fov) + '",'
    payload += '"data_location" : "' + str(data_location) + '",'
    payload += '"observing_mode" : "' + str(observing_mode) + '",'
    payload += '"process_type" : "' + str(process_type) + '",'
    payload += '"new_status" : "pending"'
    payload += "}"


    astrobase.report('adding observation : ' + str(taskid))

    try:
        astrobase.astrobase_interface.do_POST_json(resource='observations2', payload=payload)

    except Exception as err:
        astrobase.report("ERROR by *specification* : " + taskid + " has specification error...","print,slack")
        raise (Exception(str(err)))

    # add dataproducts
    add_dataproducts(astrobase, taskid, dataproducts)

    # everything is done for this new observation, put its status to 'raw'
    astrobase.astrobase_interface.do_PUT(key='observations2:new_status', id=None, taskid=taskid, value=STATUS_OBS_END)
    astrobase.report("*specification* :" + taskid + " " + STATUS_OBS_END, "print,slack")

    print(taskid)
