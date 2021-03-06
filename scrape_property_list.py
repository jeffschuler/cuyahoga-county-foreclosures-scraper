#!/usr/bin/python

import urllib2
import re
import time
import urllib
from urllib import urlencode
from BeautifulSoup import BeautifulSoup
from os import system
from os import path
from os import mkdir
import os
from xml.dom.minidom import Document
from datetime import datetime
import logging
import logging.handlers
import glob
import sys
import getopt

# Global constants
global _SITE_DIR_PATH
_SITE_DIR_PATH = '/var/www/foreclosures/sites/default/files/properties_xml'
global _ROOT_DATA_DIR_PATH
_ROOT_DATA_DIR_PATH = '/home/jeffschuler/dev/foreclosures/data'
global _ARCHIVES_DIR_PATH
_ARCHIVES_DIR_PATH = '/home/jeffschuler/dev/foreclosures/archive'
global _PROPERTY_INFO_FIELDS
_PROPERTY_INFO_FIELDS = ['sale_date', 'sale_num', 'parcel_num', 'location', 'city', 'status', 'prorated_taxes', 'case_num', 'plaintiff', 'defendant', 'address', 'description', 'appraisal', 'minimum_bid', 'sold_amount', 'purchaser', 'attorney']
global _OUTPUT_FILENAME
_OUTPUT_FILENAME = 'PROPERTIES.xml'
global _LOG_FILEPATH
_LOG_FILEPATH = '/home/jeffschuler/dev/foreclosures/log/foreclosures.log'
global _DATE_ATTRIBUTE
_DATE_ATTRIBUTE = 'date_scraped'

# Global variables
global _logger
_logger = logging.getLogger('Logger')


def usage():
    print "Usage: " + sys.argv[0] + " [-h|--help] [-q|--quiet] [-d|--deploy] [-t|--test]"
    sys.exit(2)

def soup_contents(s):
    """ check to make sure contents[0] isn't empty """
    if (isinstance(s.contents, (list, tuple)) and len(s.contents) > 0):
        return s.contents[0]
    else:
        return ''

def parse_info_table(infoTable):
    """ parse the "info" section ( <table>...</table> ) of a property entry """
    property_info = {}
    s = infoTable.contents[2].find('p')
    property_info['sale_date'] = soup_contents(s)
    s = s.findNext('p')
    property_info['sale_num'] = soup_contents(s)
    s = s.findNext('input')
    property_info['parcel_num'] = s['value']
    #_logger.debug(property_info['parcel_num'])
    s = s.findNext('p')
    property_info['location'] = soup_contents(s)
    property_info['city'] = re.sub(' ..st of River', '', soup_contents(s))
    s = s.findNext('p')
    property_info['status'] = re.sub('Status: ', '', soup_contents(s))
    property_info['status'] = re.sub('To Be Sold on .*', 'To Be Sold', property_info['status'])
    property_info['status'] = re.sub('SOLD', 'Sold', property_info['status'])
    s = s.findNext('p')
    property_info['prorated_taxes'] = re.sub('Prorated Taxes: \$', '', soup_contents(s))
    return property_info

def parse_details_table(detailsTable):
    """ parse the "details" section ( <table>...</table> ) of a property entry """
    property_info = {}
    s = detailsTable.find('p')
    s = s.findNext('p')
    property_info['case_num'] = soup_contents(s)
    s = s.findNext('p')
    s = s.findNext('p')
    property_info['plaintiff'] = soup_contents(s)
    s = s.findNext('p')
    s = s.findNext('p')
    property_info['defendant'] = soup_contents(s)
    s = s.findNext('p')
    s = s.findNext('p')
    property_info['address'] = re.sub('  $', '', soup_contents(s))
    s = s.findNext('p')
    s = s.findNext('p')
    property_info['description'] = soup_contents(s)
    s = s.findNext('p')
    if (soup_contents(s) == 'Sold Amount'):
        s = s.findNext('p')
        property_info['sold_amount'] = re.sub('\$', '', soup_contents(s))
        s = s.findNext('p')
        s = s.findNext('p')
        property_info['purchaser'] = soup_contents(s)
    elif (soup_contents(s) == 'Appraisal'):
        s = s.findNext('p')
        property_info['appraisal'] = re.sub('\$', '', soup_contents(s))
        s = s.findNext('p')
        s = s.findNext('p')
        property_info['minimum_bid'] = re.sub('\$ ', '', soup_contents(s))
    else:
        s = s.findNext('p')
    s = s.findNext('p')
    s = s.findNext('p')
    if (isinstance(s.contents, (list, tuple)) and len(s.contents) > 0):
        property_info['attorney'] = soup_contents(s)
    return property_info

def get_cities_list():
    """ get the list of cities from the menu """
    url = "http://sheriff.cuyahogacounty.us/propertysearch.asp"
    # @TODO: get all options in <select name="city">
    citiesList = [ "Bay Village", "Beachwood", "Bedford", "Bedford Heights", "Bentleyville", "Berea", "Bratenahl", "Brecksville", "Broadview Heights", "Brook Park", "Brooklyn Heights", "Brooklyn Village", "Chagrin Falls Township", "Chagrin Village", "Cleveland East of River", "Cleveland Heights", "Cleveland West of River", "Cuyahoga Heights", "East Cleveland", "Euclid", "Fairview Park", "GARFIELD", "Garfield Heights", "Gates Mills", "Glenwillow", "Highland Heights", "Highland Hills", "Hunting Valley", "Lakewood", "Lyndhurst", "Maple Heights", "Mayfield Heights", "Mayfield Village", "Middleburg Heights", "Moreland Hills", "Newburgh Heights", "North Olmsted", "North Royalton", "Oakwood", "Olmsted Falls", "Olmsted Township", "Orange", "Parma", "Parma Heights", "Pepper Pike", "Richmond Heights", "Rocky River", "Seven Hills", "Shaker Heights", "Solon", "South Euclid", "Strongsville", "University Heights", "Valley View", "Walton Hills", "Warrensville Heights", "Westlake", "Woodmere" ]
    return citiesList

def get_all_city_files(citiesList, curDataDirPath):
    """ get all city files, using the list of cities """
    for cityName in citiesList:
        get_city_file(cityName, curDataDirPath)

def get_city_file(cityName, curDataDirPath):
    """ download a city HTML file """
    cityMachineName = str.lower(re.sub(' ', '_', cityName))
    foreclosuresHtmlFilePath = os.path.join(curDataDirPath, cityMachineName + '.html')
    _logger.debug('getting: ' + foreclosuresHtmlFilePath)
    formUrl = "http://sheriff.cuyahogacounty.us/foreclosure_city.asp"
    formValues = { 'city' : cityName }
    formData = urllib.urlencode(formValues)
    formRequest = urllib2.Request(formUrl, formData)
    formRequestResponse = urllib2.urlopen(formRequest)
    cityForeclosuresHtml = formRequestResponse.read()
    foreclosuresHtmlFile = file(foreclosuresHtmlFilePath, 'w')
    foreclosuresHtmlFile.write(cityForeclosuresHtml)
    foreclosuresHtmlFile.close()
    fix_html_tables(foreclosuresHtmlFilePath)
    return foreclosuresHtmlFilePath

def parse_all_city_files(curDataDirPath, now_datetime):
    """ parse all of the city HTML files in the specified directory """
    files = glob.glob(os.path.join(curDataDirPath, '*.html'))
    for foreclosuresHtmlFilePath in files:
        filepathNoExt, ext = os.path.splitext(foreclosuresHtmlFilePath)
        xml_doc = parse_foreclosures_html(foreclosuresHtmlFilePath, now_datetime)
        output_xml_file(xml_doc, filepathNoExt + '.xml')

def parse_foreclosures_html(foreclosuresHtmlFilePath, now_datetime):
    """ parse the specified city HTML file """
    _logger.debug('parsing: ' + foreclosuresHtmlFilePath)
    foreclosuresHtmlFile = file(foreclosuresHtmlFilePath, 'r')
    xml_doc = Document()
    xml_properties = xml_doc.createElement("properties")
    xml_properties.setAttribute(_DATE_ATTRIBUTE, now_datetime.isoformat())
    xml_doc.appendChild(xml_properties)
    soup = BeautifulSoup(foreclosuresHtmlFile)
    #print soup.prettify()
    infoTable = soup.find("table", "info")
    while infoTable:
        detailsTable = infoTable.findNextSibling('table', "detail")
        property_info = parse_info_table(infoTable)
        details = parse_details_table(detailsTable)
        property_info.update(details)
        #print property_info
        # add new property record to XML doc
        xml_property = xml_doc.createElement("property")
        for field in _PROPERTY_INFO_FIELDS:
            if field in property_info:
                xml_info_item = xml_doc.createElement(field)
                item_str = xml_doc.createTextNode(str(property_info[field]))
                xml_info_item.appendChild(item_str)
                xml_property.appendChild(xml_info_item)
        xml_properties.appendChild(xml_property)
        infoTable = detailsTable.findNextSibling("table", "info")
    return xml_doc

def output_xml_file(xml_doc, outFilePath):
    """ output the xml to file """
    _logger.debug('writing: ' + outFilePath)
    outFile = file(outFilePath, 'w')
    outFile.write(xml_doc.toprettyxml(indent=""))
    outFile.close() 

def fix_html_tables(foreclosuresHtmlFilePath):
    """ after each: <table width="577px" cellpadding="2px" class="info">
    we must add a <tr> for proper parsing.
    Edit the file in place """
    replaceInFilesScript = '/home/jeffschuler/bin/replace_in_files.sh'
    findLine = '\"<table width=\\"577px\\" cellpadding=\\"2px\\" class=\\"info\\">\"'
    replaceLine = '\"<table width=\\"577px\\" cellpadding=\\"2px\\" class=\\"info\\"><tr>\"'
    replaceCommandStr = replaceInFilesScript + ' ' + foreclosuresHtmlFilePath + ' ' + findLine + ' ' + replaceLine
    system(replaceCommandStr)

def create_dirs(rootDataDirPath, now_datetime):
    """ create new data directory for the current run """
    datetimeStr = now_datetime.strftime("%Y%m%d-%H%M%S")
    curDataDirPath = os.path.join(rootDataDirPath, datetimeStr)
    os.mkdir(curDataDirPath)
    return curDataDirPath

def merge_xml_files(curDataDirPath, now_datetime):
    """ merge all of the xml properties files in the specified directory into one """
    mergedFilePath = os.path.join(curDataDirPath, _OUTPUT_FILENAME)
    _logger.debug('merging to: ' + mergedFilePath)
    xmlFilenames = glob.glob(os.path.join(curDataDirPath, '*.xml'))
    mergedFile = file(mergedFilePath, 'w')
    attribute_str = _DATE_ATTRIBUTE + '="' + now_datetime.isoformat() + '"'
    xmlHeader = '<?xml version="1.0" ?>\n<properties ' + attribute_str + '>\n'
    mergedFile.write(xmlHeader)
    mergedFile.close()
    for xmlFilename in xmlFilenames:
        # avoid processing the file we're merging into
        if re.search(_OUTPUT_FILENAME, xmlFilename):
            break
        _logger.debug('merging: ' + xmlFilename)
        # concatenate each individual file into the merged file, peel off the XML header & footer
        concatCmd = 'tail --lines=+3 ' + xmlFilename + ' | head --lines=-1 >> ' + mergedFilePath
        system(concatCmd)
    mergedFile = file(mergedFilePath, 'a')
    xmlFooter = '\n</properties>'
    mergedFile.write(xmlFooter)
    mergedFile.close() 
    return mergedFilePath

def archive_data(archivesDirPath, curDataDirPath, now_datetime):
    """ tar + gzip curDataDirPath to archives directory """
    curDataDirParent, curDataDirName = os.path.split(curDataDirPath)
    datetimeStr = now_datetime.strftime("%Y%m%d-%H%M%S")
    archiveFilename = curDataDirName + '_' + datetimeStr + '.tar.gz' # datestamp from data dir AND current datestamp
    archivePath = os.path.join(archivesDirPath, archiveFilename)
    _logger.debug('archiving to: ' + archivePath)
    system('tar -czpf ' + archivePath + ' -C ' + curDataDirParent + ' ' + curDataDirName)

def copy_to_site_dir(mergedFilePath, siteDirPath):
    """ copy the [merged xml] file to the site directory, for import """
    _logger.debug('copying to: ' + siteDirPath)
    system('cp ' + mergedFilePath + ' ' + siteDirPath)


def main(argv):
    # Global cmd-line parameter -based variables
    global _log_to_console
    _log_to_console = 1
    global _deploy
    _deploy = 0
    global _test_mode
    _test_mode = 0

    now_datetime = datetime.now()

    try:
        opts, args = getopt.getopt(argv, "hqdt", ["help", "quiet", "deploy", "test"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(2)
        elif opt in ("-q", "--quiet"):
            _log_to_console = 0
        elif opt in ("-d", "--deploy"):
            _deploy = 1
        elif opt in ("-t", "--test"):
            _test_mode = 1

    # Write messages to logfile
    _logger.setLevel(logging.DEBUG)
    handler = logging.handlers.RotatingFileHandler(_LOG_FILEPATH, maxBytes=200000, backupCount=5)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    _logger.addHandler(handler)

    # Write messages to screen
    if (_log_to_console):
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(logging.DEBUG)
        consoleFormatter = logging.Formatter("%(message)s")
        consoleHandler.setFormatter(consoleFormatter)
        _logger.addHandler(consoleHandler)

    if (_test_mode):
        curDataDirPath = '/home/jeffschuler/dev/foreclosures/data/test_data'
        parse_all_city_files(curDataDirPath, now_datetime)
        mergedFilePath = merge_xml_files(curDataDirPath, now_datetime)
        # archive_data(_ARCHIVES_DIR_PATH, curDataDirPath, now_datetime)
    else:
        curDataDirPath = create_dirs(_ROOT_DATA_DIR_PATH, now_datetime)
        citiesList = get_cities_list()
        get_all_city_files(citiesList, curDataDirPath)
        parse_all_city_files(curDataDirPath, now_datetime)
        mergedFilePath = merge_xml_files(curDataDirPath, now_datetime)
        archive_data(_ARCHIVES_DIR_PATH, curDataDirPath, now_datetime)
        if (_deploy):
            copy_to_site_dir(mergedFilePath, _SITE_DIR_PATH)

    _logger.debug('DONE')

if __name__ == "__main__":
    main(sys.argv[1:])