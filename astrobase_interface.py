#!/usr/bin/python3
import sys
import os
import requests
from requests.auth import HTTPBasicAuth
import json
import argparse
import datetime

"""
astrobase_interface.py : a commandline tool to interface with the AstroBase REST API.
"""
VERSION = "2.0"
LAST_UPDATE = "3 dec 2021"

# ====================================================================

# The request header
ASTROBASE_HEADER = {
    'content-type': "application/json",
    'cache-control': "no-cache",
    #'authorization': "Basic aedf3a3d011cd2e415ea333a523a688f30b88d26="
}

# some constants
ASTROBASE_HOST_DEV = "http://localhost:8000/astrobase"       # your local development environment with Django webserver
ASTROBASE_HOST_VM = "http://localhost:8000/astrobase"         # your local Ansible/Vagrant setup for testing
ASTROBASE_HOST_PROD = "http://192.168.178.62:8018/astrobase"      # the astrobase production environment.

DEFAULT_ASTROBASE_HOST = ASTROBASE_HOST_DEV
TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class AstroBase:
    """
    Interface class to the AstroBase REST API
    """
    def __init__(self, host, user=None, password=None):
        """
        Constructor.
        :param host: the host name of the backend.
        :param username: The username known in Django Admin.
        :param verbose: more information runtime.
        :param header: Request header for Astrobase REST requests with token authentication.
        """
        # accept some presets to set host to dev, test, acc or prod
        self.host = host
        if not self.host.endswith('/'):
            self.host += '/'

        self.header = ASTROBASE_HEADER
        self.user = user
        self.password = password

    def do_print(self, info_str):
        timestamp = datetime.datetime.now().strftime(TIME_FORMAT)
        print(str(timestamp)+ ' - '+info_str)

    # === Backend requests ================================================================================

    def encodePayload(self, payload):
        """

        The POST body does not simply accept a payload dict, it needs to be translated to a string with some
        peculiarities
        :param payload:
        :return: payload_string
        """

        payload_string = str(payload).replace("'","\"")
        #payload_string = payload_string.replace(",", ",\n")

        # reconstruct the lists by moving the brackets outside the double quotes
        payload_string = payload_string.replace("\"[", "[\"")
        payload_string = payload_string.replace("]\"", "\"]")
        payload_string = payload_string.replace("/,", "/\",\"")
        payload_string = payload_string.replace("u\"", "\"")

        self.do_print("The payload_string: [" + payload_string + "]")
        return payload_string


    def GET_TaskObjectByTaskId(self, resource, taskid):
        """
        Do a http GET request to the alta backend to find the Observation with the given runId
        :runId runId:
        """

        url = self.host + resource
        # create the querystring, external_ref is the mapping of this element to the alta datamodel lookup field
        querystring = {"taskID": taskid}

        response = requests.request("GET", url, headers=self.header, params=querystring)
        self.do_print("[GET " + response.url + "]")

        try:
            json_response = json.loads(response.text)
            results = json_response["results"]
            taskobject = results[0]
            return taskobject
        except:
            raise (Exception(
                "ERROR: " + str(response.status_code) + ", " + str(response.reason) + ', ' + str(response.content)))

    # ------------------------------------------------------------------------------#
    #                                Main User functions                            #
    # ------------------------------------------------------------------------------#


    def do_GET_ID(self, key, value):
        """
        Get the id based on a field value of a resource. This is a generic way to retrieve the id.
        :param resource: contains the resource, for example 'observations', 'dataproducts'
        :param field: the field to search on, this will probably be 'name' or 'filename'
        :param value: the value of the 'field' to search on.
        :return id
        """

        # split key in resource and field
        params = key.split(":")
        resource = params[0]
        field = params[1]

        url = self.host + resource + "?" + field + "=" + value
        response = requests.request("GET", url, headers=self.header)
        self.do_print("[GET " + response.url + "]")
        self.do_print("Response: " + str(response.status_code) + ", " + str(response.reason))

        try:
            json_response = json.loads(response.text)
            results = json_response["results"]
            result = results[0]
            id = result['id']
            return id
        except:
            return '-1'
            #raise (Exception("ERROR: " + response.url + " not found."))


    def do_GET(self, key, id=None, taskid=None):
        """
        Do a http GET request to the astrobase backend to find the value of one field of an object
        :param key: contains the name of the resource and the name of the field separated by a colon.
        :param id: the database id of the object.
        :param taskid (optional): when the taskid (of an activity) is known it can be used instead of id.
        """

        # split key in resource and field
        params = key.split(":")
        resource = params[0]
        field = params[1]

        if taskid!=None:
            taskObject = self.GET_TaskObjectByTaskId(resource, taskid)
            id = taskObject['id']

        if id==None:
            # give up and throw an exception.
            raise (Exception("ERROR: no valid 'id' or 'taskid' provided"))

        url = self.host + resource + "/" + str(id) + "/"
        self.do_print(('url: ' + url))

        response = requests.request("GET", url, headers=self.header)
        self.do_print("[GET " + response.url + "]")
        self.do_print("Response: " + str(response.status_code) + ", " + str(response.reason))

        try:
            json_response = json.loads(response.text)
            value = json_response[field]
            return value
        except Exception as err:
          self.do_print("Exception : " + str(err))
          raise (
              Exception("ERROR: " + str(response.status_code) + ", " + str(response.reason) + ', ' + str(response.content)))


    #  python astrobase_interface.py -o GET_LIST --key observations:taskID --query status=valid
    def do_GET_LIST(self, key, query):
        """
        Do a http GET request to the astrobase backend to find the value of one field of an object
        :param key: contains the name of the resource and the name of the field separated by a dot.
        :param id: the database id of the object.
        :param taskid (optional): when the taskid (of an activity) is known it can be used instead of id.
        """
        self.do_print("do_GET_LIST(" + key + "," + query + ")")
        # split key in resource and field
        params = key.split(":")
        resource = params[0]
        field = params[1]

        url = self.host + resource + "?" + str(query)
        # self.verbose_print("url = " + url)

        response = requests.request("GET", url, headers=self.header)
        self.do_print("[GET " + response.url + "]")
        self.do_print("Response: " + str(response.status_code) + ", " + str(response.reason))

        try:
            json_response = json.loads(response.text)
            results = json_response["results"]
            #results = json.loads(response.text)
            # loop through the list of results and extract the requested field (probably taskID),
            # and add it to the return list.
            list = []
            for result in results:
                value = result[field]
                list.append(value)

            return list
        except Exception as err:
            self.do_print("Exception : " + str(err))
            raise (Exception(
                "ERROR: " + str(response.status_code) + ", " + str(response.reason) + ', ' + str(response.content)))


    def do_GET_NextTaskID(self, timestamp, taskid_postfix=""):
        """
        :param timestamp: timestamp on which the taskid is based
        :param taskid_postfix: optional addition to the taskid,
               like when taskid_postfix="_IMG" the taskid will become "190405001_IMG"
        :return: taskid
        """

        self.do_print("do_GET_NextTaskID(" + str(timestamp) + ")")

        # construct the url
        url = self.host + "get_next_taskid?timestamp=" + str(timestamp)+"&taskid_postfix="+taskid_postfix

        # do the request to the astrobase backend
        response = requests.request("GET", url, headers=self.header)
        self.do_print("[GET " + response.url + "]")
        self.do_print("Response: " + str(response.status_code) + ", " + str(response.reason))

        # parse the response
        try:
            json_response = json.loads(response.text)
            taskID = json_response["taskID"]
            return taskID
        except Exception as err:
            self.do_print("Exception : " + str(err))
            raise (Exception(
                "ERROR: " + str(response.status_code) + ", " + str(response.reason) + ', ' + str(response.content)))


    def do_GET_Observation(self, taskid):
        """
        Do a http request to the astrobase backend get all the observation parameters in the response
        :param taskid
        """
        self.do_print("do_GET_Observation(" + taskid + ")")

        # construct the url
        url = self.host + "observations?taskID=" + str(taskid)

        # do the request to the astrobase backend
        response = requests.request("GET", url, headers=self.header)
        self.do_print("[GET " + response.url + "]")

        # parse the response
        try:
            json_response = json.loads(response.text)
            results = json_response["results"]
            observation = results[0]
            return observation
        except Exception as err:
            self.do_print("Exception : " + str(err))
            raise (Exception(
                "ERROR: " + str(response.status_code) + ", " + str(response.reason) + ', ' + str(response.content)))


    def do_PUT(self, key='observations', id=None, value=None, taskid=None):
        """
        PUT a value to an existing field of a resource (table).
        :param key: contains the name of the resource and the name of the field separated by a dot. observations.description
        :param id: the database id of the object.
        :param value: the value that has to be PUT in the key. If omitted, an empty put will be done to trigger the signals.
        :param taskid (optional): when the taskid of an observation is known it can be used instead of id.
        """

        # split key in resource and field
        if key.find(':')>0:
            params = key.split(":")
            resource = params[0]
            field = params[1]
        else:
            resource = key
            field = None

        if taskid != None:
            taskObject = self.GET_TaskObjectByTaskId(resource, taskid)
            id = taskObject['id']

        url = self.host + resource + "/" + str(id) + "/"
        if id==None:
            raise (Exception("ERROR: no valid 'id' or 'taskid' provided"))

        payload = {}
        if field!=None:
            payload[field]=value
            payload = self.encodePayload(payload)
        try:
            if self.user == None:
                response = requests.request("PUT", url, data=payload, headers=self.header)
            else:
                response = requests.request("PUT", url, data=payload, headers=self.header, auth=HTTPBasicAuth(self.user, self.password))

            self.do_print("[PUT " + response.url + "]")
            self.do_print("Response: " + str(response.status_code) + ", " + str(response.reason))
        except:
            raise (Exception(
                "ERROR: " + str(response.status_code) + ", " + str(response.reason) + ', ' + str(response.content)))


    # do_PUT_LIST(key = observations:new_status, taskid = 180223003, value = valid)
    def do_PUT_LIST(self, key='dataproducts', taskid=None, value=None):
        """
        PUT a value to an existing field of  resource (table).
        :param key: contains the name of the resource and the name of the field separated by a colon. observations:new_status
        :param value: the value that has to be PUT in the key. If omitted, an empty put will be done to trigger the signals.
        :param taskid: the value is PUT to all objects with the provided taskid
        """

        # split key in resource and field
        if key.find(':')>0:
            params = key.split(":")
            resource = params[0]
            field = params[1]
        else:
            resource = key
            field = None

        get_key = resource+':id'
        get_query= 'taskID='+taskid
        ids = self.do_GET_LIST(get_key,get_query)

        for id in ids:
            url = self.host + resource + "/" + str(id) + "/"
            self.do_print(('url: ' + url))

            payload = {}
            if field!=None:
                payload[field]=value
                payload = self.encodePayload(payload)
            try:
                if self.user == None:
                    response = requests.request("PUT", url, data=payload, headers=self.header)
                else:
                    response = requests.request("PUT", url, data=payload, headers=self.header, auth = HTTPBasicAuth(self.user, self.password))

                self.do_print("[PUT " + response.url + "]")
                self.do_print("Response: " + str(response.status_code) + ", " + str(response.reason))
            except:
                raise (Exception(
                    "ERROR: " + str(response.status_code) + ", " + str(response.reason) + ', ' + str(response.content)))



    def do_POST_json(self, resource, payload):
        """
        POST a payload to a resource (table). This creates a new object (observation or dataproduct)
        This function replaces the old do_POST function that still needed to convert the json content in a very ugly
        :param resource: contains the resource, for example 'observations', 'dataproducts'
        :param payload: the contents of the object to create in json format
        """

        url = self.host + resource + '/'
        self.do_print(('payload: ' + payload))

        try:
            if self.user==None:
                response = requests.request("POST", url, data=payload, headers=self.header)
            else:
                response = requests.request("POST", url, data=payload, headers=self.header, auth=HTTPBasicAuth(self.user, self.password))

            self.do_print("[POST " + response.url + "]")
            self.do_print("Response: " + str(response.status_code) + ", " + str(response.reason))
            if not (response.status_code==200 or response.status_code==201):
                raise Exception()
        except Exception:
            raise (Exception("ERROR: " + str(response.status_code) + ", " + str(response.reason) + ', ' + str(response.content)))


    def do_POST_dataproducts(self, taskid, dataproducts):
        """
        POST (create) a batch of dataproducts for the (observation) with the given taskid.
        This is done with a custom made http request to the AstroBase backend
        :param taskid: taskid of the observation
        :param dataproducts: json list of dataproducts to be added to the provided taskid
        """

        # is 'dataproducts' a valid list of dataproducts?
        try:
            number_of_dataproducts = len(dataproducts)
            self.do_print("do_POST_dataproducts(" + taskid + "," + str(number_of_dataproducts) + ")")
        except Exception as err:
            raise (Exception(
                "ERROR: " + str(err)))

        # construct the url
        url = self.host + "post_dataproducts?taskID=" + str(taskid)

        # encode the dictonary as proper json
        payload = self.encodePayload(dataproducts)
        try:
            # do a POST request to the 'post_dataproducts' resource of the astrobase backend
            if self.user == None:
                response = requests.request("POST", url, data=payload, headers=self.header)
            else:
                response = requests.request("POST", url, data=payload, headers=self.header, auth = HTTPBasicAuth(self.user, self.password))

            self.do_print("[POST " + response.url + "]")

            # if anything went wrong, throw an exception.
            if not (response.status_code==200 or response.status_code==201):
                raise Exception(str(response.status_code) + " - " + str(response.reason))
        except Exception as err:
            raise (Exception("ERROR: " + str(err)))

        # if it has all succeeded, give back the taskid as an indication of success
        return taskid


    def do_DELETE(self, resource, id):
        """
        Do a http DELETE request to the AstroBase backend
        """
        if id == None:
            raise (Exception("ERROR: no valid 'id' provided"))

        # if a range of ID's is given then do multiple deletes
        if (str(id).find('..')>0):
            self.do_print("Deleting " + str(id) + "...")
            s = id.split('..')
            start = int(s[0])
            end = int(s[1]) + 1
        else:
            # just a single delete
            start = int(id)
            end = int(id) + 1

        for i in range(start,end):
            url = self.host + resource + "/" + str(i) + "/"

            try:
                if self.user==None:
                    response = requests.request("DELETE", url, headers=self.header)
                else:
                    response = requests.request("DELETE", url, headers=self.header, auth = HTTPBasicAuth(self.user, self.password))

                    self.do_print("[DELETE " + response.url + "]")
                self.do_print("Response: " + str(response.status_code) + ", " + str(response.reason))
            except:
                raise (Exception("ERROR: deleting " + url + "failed." + response.url))


# ------------------------------------------------------------------------------#
#                                Module level functions                         #
# ------------------------------------------------------------------------------#
def exit_with_error(message):
    """
    Exit the code for an error.
    :param message: the message to print.
    """
    print(message)
    sys.exit(-1)


def get_arguments(parser):
    """
    Gets the arguments with which this application is called and returns
    the parsed arguments.
    If a parfile is give as argument, the arguments will be overrided
    The args.parfile need to be an absolute path!
    :param parser: the argument parser.
    :return: Returns the arguments.
    """
    args = parser.parse_args()
    if args.parfile:
        args_file = args.parfile
        if os.path.exists(args_file):
            parse_args_params = ['@' + args_file]
            # First add argument file
            # Now add command-line arguments to allow override of settings from file.
            for arg in sys.argv[1:]:  # Ignore first argument, since it is the path to the python script itself
                parse_args_params.append(arg)
            print(parse_args_params)
            args = parser.parse_args(parse_args_params)
        else:
            raise (Exception("Can not find parameter file " + args_file))
    return args
