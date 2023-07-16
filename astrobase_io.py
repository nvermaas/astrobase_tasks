"""
    File name: astrobase_io.py
    Authors: Nico Vermaas
    Date created: 2021-12-03
    Description: This is the IO class to communicate with astrobase
                 It also has functionality to write to slack, stdout and logging.
"""

import os
import subprocess
import datetime
import requests
import logging

logger = logging.getLogger(__name__)

from astrobase_interface import AstroBase

# The request header
ASTROBASE_HEADER = {
    'content-type': "application/json",
    'cache-control': "no-cache",
}


class AstroBaseIO:
    """
    This is the IO class for the astrobase_services that handles the communication
    with AstroBase and the astrometry.net services. 
    It also has functionality to write to slack, stdout and logging.
    """
    TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

    def __init__(self, astrobase_host, user=None, password=None):
        """
        Constructor.
        :param host: the host name of the backend.
        :param username: The username known in Django Admin.
        """

        # accept some presets to set host to dev, test, acc or prod
        self.host = astrobase_host

        if (not self.host.endswith('/')):
            self.host += '/'

        self.header = ASTROBASE_HEADER
        self.user = user
        self.password = password

        self.astrobase_interface = AstroBase(self.host, self.user, self.password)


    def do_print(self, info_str):
        timestamp = datetime.datetime.now().strftime(self.TIME_FORMAT)
        print(str(timestamp)+ ' - '+info_str)


# --------------------------------------------------------------------------------------------------------
    def report(self, message, method='logging'):
        #self.do_print(message)
        if 'ERROR' in message.upper():
            logging.error(message)
        else:
            logging.info(message)

        if 'print' in method:
            self.do_print(message)

        if 'slack' in method:
            self.do_print(message)
            self.send_message_to_apidorn_slack_channel(message)

    def send_message_to_apidorn_slack_channel(self, message_str):
        """
        Send a message to the Slack channel #atdb-logging
        With this channel a notification of Ingest ready (or failed) is given.
        Don't raise an Exception in case of error
        :param message_str: Message String
        """
        try:
            timestamp = datetime.datetime.now().strftime(self.TIME_FORMAT)
            payload = {"text": str(timestamp) + ' - ' + message_str}

            # this no longer works, because the repo became public... never mind for now.
            url = "https://hooks.slack.com/services/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"
            res = requests.post(url, data=str(payload))
        except Exception as err:
            print("Error sending message to slack: " + str(err))