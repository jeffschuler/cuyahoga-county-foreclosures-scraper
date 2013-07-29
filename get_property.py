#!/usr/bin/python

# Shell
import sys
import argparse

# Fetching
import urllib2
import urllib
import cookielib

# Parsing
import string
import re
from bs4 import BeautifulSoup

# Data storage
import datetime
from pymongo import MongoClient

# Debug
import logging
import logging.handlers
#import pprint


# Logging
global _LOG_FILE_PATH
_LOG_FILE_PATH = 'log/get_property.log'
global _logger
_logger = logging.getLogger('Logger')


# Output data
global _OUTPUT_DIR
_OUTPUT_DIR = 'data'


# Pretty-Printer
#global _pp
#_pp = pprint.PrettyPrinter(indent=2)


# Run live search or use pre-saved data
global _LIVE_MODE
_LIVE_MODE = False


def set_up_logger(log_file_path):
    # Log to console
    #consoleHandler = logging.StreamHandler()
    #consoleHandler.setLevel(logging.DEBUG)
    #consoleFormatter = logging.Formatter("%(message)s")
    #consoleHandler.setFormatter(consoleFormatter)
    #_logger.addHandler(consoleHandler)

    # Log to logfile
    _logger.setLevel(logging.DEBUG)
    handler = logging.handlers.RotatingFileHandler(log_file_path, maxBytes=200000, backupCount=5)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    _logger.addHandler(handler)


def get_dynamic_form_vars(page_html):
    """Get necessary dynamic, session-based variables from page."""
    soup = BeautifulSoup(page_html)

    event_validation = soup.find("input", {"name": "__EVENTVALIDATION"}).get('value')
    view_state = soup.find("input", {"name": "__VIEWSTATE"}).get('value')

    return {
        '__EVENTVALIDATION': event_validation,
        '__VIEWSTATE': view_state
    }


def run_parcel_search(parcel_num):
    """Submit form to search for a single parcel number, and return response."""

    _logger.debug('getting parcel #' + parcel_num)

    base_url = 'http://sheriff.cuyahogacounty.us/en-US'
    page_url = base_url + '/Foreclosure-Property-Search.aspx'
    form_url = base_url + '/PropertySearch.aspx?LanguageCD=en-US&ItemKey=26945&pb=y'

    # Load page once to establish cookies and get session-based form variables.
    jar = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
    urllib2.install_opener(opener)
    response = opener.open(page_url).read()
    form_values = get_dynamic_form_vars(response)
    #_pp.pprint(jar)

    form_values.update({
        'ctl00$ctl04': 'ctl00$ContentPlaceHolder1$UpdatePanel1|ctl00$ContentPlaceHolder1$btnSearchForeclosureProperties',
        'ctl00$ContentPlaceHolder1$txtParcelNumber': parcel_num,
        'ctl00$ContentPlaceHolder1$TextBoxWatermarkExtender1_ClientState': '',
        'ctl00$ContentPlaceHolder1$MaskedEditExtenderParcelNumber_ClientState': '',
        'ctl00$ContentPlaceHolder1$txtStartSaleDate': '',
        'ctl00$ContentPlaceHolder1$txtEndSaleDate': '',
        'ctl00$ContentPlaceHolder1$ddlCity': '0',
        'ctl00$ctl11': 'nnennnn',
        '__ASYNCPOST': 'true',
        'ctl00$ContentPlaceHolder1$btnSearchForeclosureProperties': '.',
        '__AjaxControlToolkitCalendarCssLoaded': '',
        'ctl00_masterNav_Menu1_ClientState': '',
        'ctl00$SiteSearch1$txtTerms': '',
        'par_id': '',
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
    })

    print form_values

    form_data = urllib.urlencode(form_values)

    request = urllib2.Request(form_url, form_data)
    request.get_full_url()
    request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:22.0) Gecko/20100101 Firefox/22.0')
    request.add_header('X-MicrosoftAjax', 'Delta=true')  # Necessary for postback
    request.add_header('Referer', 'http://sheriff.cuyahogacounty.us/en-US/Foreclosure-Property-Search.aspx')
    response = opener.open(request).read()

    return response


def normalize_parcel_num(parcel_num):
    """
    Use consistent format for parcel numbers by stripping dashes.
    The form doesn't care whether there are dashes or not.
    """
    return string.replace(parcel_num, '-', '')


def write_to_file(data, data_dir, filename):
    """Write data to a file in our data directory."""
    outfile_path = data_dir + '/' + filename
    outfile = file(outfile_path, 'w')
    outfile.write(data)
    outfile.close()
    return outfile_path


def read_from_file(data_dir, filename):
    """Read and return all data from a file in our data directory."""
    path = data_dir + '/' + filename
    infile = file(path, 'r')
    data = infile.read()
    infile.close()
    return data


def save_response(response, parcel_num, data_dir):
    """Save response to file."""
    filename = parcel_num + '-orig.txt'
    return write_to_file(response, data_dir, filename)


def get_search_response_from_file(parcel_num, data_dir):
    """Read a pre-saved (original) response from existing file."""
    filename = parcel_num + '-orig.txt'
    return read_from_file(data_dir, filename)


def parse_num_properties(response):
    """Get the number of properties returned from within the response."""
    m = re.search('<span id="ctl00_ContentPlaceHolder1_lblNumberOfRecordsFound">(\d*)</span>', response)
    if m is None:
        _logger.debug('Error: Form response did not include foreclosure records table.')
        return 0
    elif len(m.groups()) > 0:
        return int(m.group(1))
    else:
        _logger.debug('No foreclosure records returned.')
        return 0


def clean_response(response):
    """
    Clean up and return the search response.
    It comes with initial data before and after the HTML. Remove that,
    then prettify with BeautifulSoup.
    """

    # Remove non-HTML first line
    parts = string.split(response, "\n", 1)
    response = parts[1]

    # Remove non-HTML at the end, from "|0|hiddenField|__EVENTTARGET|" on
    end_html_index = string.find(response, '|0|hiddenField|__EVENTTARGET|')
    response = response[0:end_html_index]

    # Prettify with BeautifulSoup.
    soup = BeautifulSoup(response)
    response = soup.prettify()

    return response


def parse_properties(response, num_properties):
    soup = BeautifulSoup(response)
    #results_table = soup.find(id="ctl00_ContentPlaceHolder1_gvSearchResult")
    id_prefix_base = "ctl00_ContentPlaceHolder1_gvSearchResult_ctl"
    results = [{} for i in range(num_properties)]
    i = 0
    for result in results:
        table_index = str(i + 2).zfill(2)  # Zero-pad index to two characters
        id_prefix = id_prefix_base + table_index + "_lbl"
        result['parcel_num'] = string.strip(soup.find(id=id_prefix + "ParcelNumber").string)
        result['sale_date'] = string.strip(soup.find(id=id_prefix + "SaleDate").string)
        result['sale_number'] = string.strip(soup.find(id=id_prefix + "SaleNumber").string)
        result['case_number'] = string.strip(soup.find(id=id_prefix + "CaseNumber").string)
        result['result'] = string.strip(soup.find(id=id_prefix + "Result").string)
        result['sold_amount'] = string.strip(soup.find(id=id_prefix + "SoldAmt").string)
        if soup.find(id=id_prefix + "MinBid"):
            result['minimum_bid'] = string.strip(soup.find(id=id_prefix + "MinBid").string)
        i += 1
    return results


def store_properties_info_in_db(parsed_data):
    for property in parsed_data:
        store_parcel_record_in_db(property)
    return


def store_parcel_record_in_db(parcel_record):
    client = MongoClient()
    db = client.foreclosures
    parcel_infos = db.parcel_info
    parcel_record['date'] = datetime.datetime.utcnow()
    parcel_info_id = parcel_infos.insert(parcel_record)
    return parcel_info_id


def get_parcel_info(parcel_num, data_dir=_OUTPUT_DIR, live_mode=_LIVE_MODE):
    """Submit the form, output to file, and parse."""
    parcel_num = normalize_parcel_num(parcel_num)
    if live_mode:
        response = run_parcel_search(parcel_num)
        outfile_path = save_response(response, parcel_num, data_dir)
        print "Original response saved to '" + outfile_path + "'."
    else:
        response = get_search_response_from_file(parcel_num, data_dir)

    num_properties = parse_num_properties(response)
    print str(num_properties) + " Property records returned."

    response = clean_response(response)
    cleaned_response_path = write_to_file(response, data_dir, parcel_num + '.html')
    print "Cleaned-up response saved to '" + cleaned_response_path + "'."

    return parse_properties(response, num_properties)


def main(argv):
    parser = argparse.ArgumentParser(description='Search for parcel information.')
    parser.add_argument('-c', '--cached',
                        help='Cached mode: get parcel info from file.',
                        action='store_true')
    parser.add_argument('-l', '--logfile',
                        help='Path to writable logfile. Defaults to "./log/get_property.log"',
                        default=_LOG_FILE_PATH)
    parser.add_argument('-d', '--data_dir',
                        help='Path to data directory. No trailing slash. Defaults to "./data"',
                        default=_OUTPUT_DIR)
    parser.add_argument('parcel_num',
                        help='Parcel number, with or without dashes, like "007-09-107".')

    args = parser.parse_args()

    # Logfile path arg
    if args.logfile:
        log_file_path = args.logfile
    else:
        log_file_path = _LOG_FILE_PATH
    set_up_logger(log_file_path)

    # Data directory path arg
    if args.data_dir:
        data_dir = args.data_dir
    else:
        data_dir = _OUTPUT_DIR

    # Parcel number arg
    parcel_num = args.parcel_num
    print 'Getting information for parcel: ' + parcel_num
    if args.cached:
        live_mode = False
        print 'Running in cached mode.'
    else:
        live_mode = True

    # Go!
    properties = get_parcel_info(parcel_num, data_dir, live_mode)
    if live_mode:
        store_properties_info_in_db(properties)
    print properties


if __name__ == "__main__":
    main(sys.argv[1:])
