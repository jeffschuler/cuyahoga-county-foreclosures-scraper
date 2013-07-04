#!/usr/bin/python

import urllib2
import urllib
import logging
import logging.handlers

# Logging
global _LOG_FILEPATH
_LOG_FILEPATH = 'log/get_property.log'

global _logger
_logger = logging.getLogger('Logger')

# Log to console
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.DEBUG)
consoleFormatter = logging.Formatter("%(message)s")
consoleHandler.setFormatter(consoleFormatter)
_logger.addHandler(consoleHandler)

# Log to logfile
_logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(_LOG_FILEPATH, maxBytes=200000, backupCount=5)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
_logger.addHandler(handler)


def get_parcel_info(parcel_num):
    _logger.debug('getting parcel #' + parcel_num)
    formUrl = "http://sheriff.cuyahogacounty.us/en-US/Foreclosure-Property-Search.aspx"
    formValues = {'ctl00_ContentPlaceHolder1_txtParcelNumber': parcel_num}
    formData = urllib.urlencode(formValues)
    formRequest = urllib2.Request(formUrl, formData)
    formRequestResponse = urllib2.urlopen(formRequest)
    formRequestResponseHtml = formRequestResponse.read()
    return formRequestResponseHtml

# @TODO:
# Parse "Number of Properties Found: \d"
# get table
# parse Sale Date, Sale Number, Case Number Status
# click View
# get other details
