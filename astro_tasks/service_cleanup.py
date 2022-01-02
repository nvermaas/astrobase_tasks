"""
    File name: cleanup.py
    Author: Nico Vermaas
    Date created: 2019-10-20
    Description: - removes data
"""

import os
import shutil

# --- Main Service -----------------------------------------------------------------------------------------------

def do_cleanup(astrobaseIO, local_data_dir):

    query = 'my_status=removing'
    taskIDs = astrobaseIO.astrobase_interface.do_GET_LIST(key='observations2:taskID', query=query)

    if len(taskIDs) > 0:

        # loop through the 'removing' observations
        for taskID in taskIDs:

            task_directory = os.path.join(local_data_dir, taskID)

            if os.path.exists(task_directory):
                shutil.rmtree(task_directory)
                astrobaseIO.report("*cleanup* : removing " + task_directory, "slack")

            # remove the observation and its dataproducts from the database
            id = astrobaseIO.astrobase_interface.do_GET_ID('observations2:taskID',taskID)
            astrobaseIO.astrobase_interface.do_DELETE('observations2',id)
