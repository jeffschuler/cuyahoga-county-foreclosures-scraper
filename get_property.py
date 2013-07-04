#!/usr/bin/python

import urllib2
import urllib
import logging
import logging.handlers
import cookielib

import pprint

# Logging
global _LOG_FILEPATH
_LOG_FILEPATH = 'log/get_property.log'

global _logger
_logger = logging.getLogger('Logger')

# Log to console
#consoleHandler = logging.StreamHandler()
#consoleHandler.setLevel(logging.DEBUG)
#consoleFormatter = logging.Formatter("%(message)s")
#consoleHandler.setFormatter(consoleFormatter)
#_logger.addHandler(consoleHandler)

# Log to logfile
_logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(_LOG_FILEPATH, maxBytes=200000, backupCount=5)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
_logger.addHandler(handler)

# Pretty-Printer
pp = pprint.PrettyPrinter(indent=2)

def get_parcel_info(parcel_num):
    _logger.debug('getting parcel #' + parcel_num)

    base_url = 'http://sheriff.cuyahogacounty.us/en-US'
    page_url = base_url + '/Foreclosure-Property-Search.aspx'
    form_url = base_url + '/PropertySearch.aspx?LanguageCD=en-US&ItemKey=26945&pb=y'

    jar = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
    urllib2.install_opener(opener)
    #r = opener.open(base_url)
    urllib2.urlopen(page_url)
    pp.pprint(jar)

    #form_values = {'ctl00_ContentPlaceHolder1_txtParcelNumber': parcel_num}
    form_values = {
      'ctl00$ctl04': 'ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHolder1$btnSearchForeclosureProperties',
      'ctl00$ContentPlaceHolder1$txtParcelNumber': parcel_num,
      'ctl00$ContentPlaceHolder1$TextBoxWatermarkExtender1_ClientState': None,
      'ctl00$ContentPlaceHolder1$MaskedEditExtenderParcelNumber_ClientState': None,
      'ctl00$ContentPlaceHolder1$ddlCity': None,
      'ctl00$ctl11': 'nnennnn'
      }
    form_data = urllib.urlencode(form_values)

    form_request = urllib2.Request(form_url, form_data)
    form_response = urllib2.urlopen(form_request)
    response_html = form_response.read()

    outfile_path = 'data/' + parcel_num + '.html'
    outfile = file(outfile_path, 'w')
    outfile.write(response_html)
    outfile.close()

    return outfile_path

# @TODO:
# Parse return:
#   #ctl00_ContentPlaceHolder1_pnlResultPanel
# get table
# "Number of Properties Found: \d"
#   #ctl00_ContentPlaceHolder1_lblNumberOfRecordsFound
# parse Sale Date, Sale Number, Case Number Status
# click View
# get other details
