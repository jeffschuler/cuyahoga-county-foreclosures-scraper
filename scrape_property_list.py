#!/usr/bin/python

import os
import urllib2, re, time
import urllib
from urllib import urlencode
from BeautifulSoup import BeautifulSoup
from os import system
from xml.dom.minidom import Document
from datetime import datetime
import logging
import logging.handlers

# Write messages to logfile
LOG_FILEPATH = '/home/jeffschuler/dev/foreclosures/log/foreclosures.log'
logger = logging.getLogger('Logger')
logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(LOG_FILEPATH, maxBytes=200000, backupCount=5)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Write messages to screen
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.DEBUG)
consoleFormatter = logging.Formatter("%(message)s")
consoleHandler.setFormatter(consoleFormatter)
logger.addHandler(consoleHandler)


property_info_fields = ['sale_date', 'sale_num', 'parcel_num', 'location', 'city', 'status', 'prorated_taxes', 'case_num', 'plaintiff', 'defendant', 'address', 'description', 'appraisal', 'minimum_bid', 'sold_amount', 'purchaser', 'attorney']

def soup_contents(s):
    # check to make sure contents[0] isn't empty
    if (isinstance(s.contents, (list, tuple)) and len(s.contents) > 0):
        return s.contents[0]
    else:
        return ''

def parse_info_table(infoTable):
    property_info = {}
    s = infoTable.contents[2].find('p')
    property_info['sale_date'] = soup_contents(s)
    s = s.findNext('p')
    property_info['sale_num'] = soup_contents(s)
    s = s.findNext('input')
    property_info['parcel_num'] = s['value']
    #logger.debug(property_info['parcel_num'])
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
    url = "http://sheriff.cuyahogacounty.us/propertysearch.asp"
    # get all options in <select name="city">
    citiesList = [ "Bay Village", "Beachwood", "Bedford", "Bedford Heights", "Bentleyville", "Berea", "Bratenahl", "Brecksville", "Broadview Heights", "Brook Park", "Brooklyn Heights", "Brooklyn Village", "Chagrin Falls Township", "Chagrin Village", "Cleveland East of River", "Cleveland Heights", "Cleveland West of River", "Cuyahoga Heights", "East Cleveland", "Euclid", "Fairview Park", "GARFIELD", "Garfield Heights", "Gates Mills", "Glenwillow", "Highland Heights", "Highland Hills", "Hunting Valley", "Lakewood", "Lyndhurst", "Maple Heights", "Mayfield Heights", "Mayfield Village", "Middleburg Heights", "Moreland Hills", "Newburgh Heights", "North Olmsted", "North Royalton", "Oakwood", "Olmsted Falls", "Olmsted Township", "Orange", "Parma", "Parma Heights", "Pepper Pike", "Richmond Heights", "Rocky River", "Seven Hills", "Shaker Heights", "Solon", "South Euclid", "Strongsville", "University Heights", "Valley View", "Walton Hills", "Warrensville Heights", "Westlake", "Woodmere" ]
    #citiesList = [ "Cleveland West of River" ]
    return citiesList

def get_all_city_files(citiesList, curDataDirPath):
    for cityName in citiesList:
        get_city_file(cityName, curDataDirPath)

def get_city_file(cityName, curDataDirPath):
    cityMachineName = str.lower(re.sub(' ', '_', cityName))
    foreclosuresHtmlFilePath = os.path.join(curDataDirPath, cityMachineName + '.html')
    logger.debug('getting: ' + foreclosuresHtmlFilePath)
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

def parse_all_city_files(curDataDirPath):
    for subdir, dirs, files in os.walk(curDataDirPath): # use glob.glob instead?
        for filename in files:
            basename, extension = os.path.splitext(filename)
            if (extension == '.html'):
                foreclosuresHtmlFilePath = os.path.join(subdir, filename)
                logger.debug('parsing: ' + foreclosuresHtmlFilePath)
                xml_doc = parse_foreclosures_html(foreclosuresHtmlFilePath)
                output_xml_file(xml_doc, curDataDirPath, basename + '.xml')

def parse_foreclosures_html(foreclosuresHtmlFilePath):
    foreclosuresHtmlFile = file(foreclosuresHtmlFilePath, 'r')
    xml_doc = Document()
    xml_properties = xml_doc.createElement("properties")
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
        for field in property_info_fields:
            if field in property_info:
                xml_info_item = xml_doc.createElement(field)
                item_str = xml_doc.createTextNode(property_info[field])
                xml_info_item.appendChild(item_str)
                xml_property.appendChild(xml_info_item)
        xml_properties.appendChild(xml_property)
        infoTable = detailsTable.findNextSibling("table", "info")
    return xml_doc

def output_xml_file(xml_doc, curDataDirPath, outFileName):
    outFilePath = os.path.join(curDataDirPath, outFileName)
    logger.debug('writing: ' + outFilePath)
    outFile = file(outFilePath, 'w')
    outFile.write(xml_doc.toprettyxml(indent=""))
    outFile.close() 

def fix_html_tables(foreclosuresHtmlFilePath):
    # after each: <table width="577px" cellpadding="2px" class="info">
    # we must add a <tr> for proper parsing
    # Edits file in place
    replaceInFilesScript = '/home/jeffschuler/bin/replace_in_files.sh'
    findLine = '\"<table width=\\"577px\\" cellpadding=\\"2px\\" class=\\"info\\">\"'
    replaceLine = '\"<table width=\\"577px\\" cellpadding=\\"2px\\" class=\\"info\\"><tr>\"'
    replaceCommandStr = replaceInFilesScript + ' ' + foreclosuresHtmlFilePath + ' ' + findLine + ' ' + replaceLine
    system(replaceCommandStr)

def create_dirs(rootDataDir):
    datetimeStr = datetime.now().strftime("%Y%m%d-%H%M%S")
    curDataDirPath = rootDataDir + datetimeStr
    os.mkdir(curDataDirPath)
    return curDataDirPath

#def merge_xml_files(curDataDirPath):
#    print "merge_xml_files"
#    #return outFilePath
#
#def copy_to_site_dir():
#    print "copy_to_site_dir"


rootDataDir = '/home/jeffschuler/dev/foreclosures/data/'
#curDataDirPath = '/home/jeffschuler/dev/foreclosures/data/20101104-230232' #@DEBUG
curDataDirPath = create_dirs(rootDataDir)
citiesList = get_cities_list()
get_all_city_files(citiesList, curDataDirPath)
parse_all_city_files(curDataDirPath)
#parse_foreclosures_html('/home/jeffschuler/dev/foreclosures/data/20101104-230232/cleveland_east_of_river.html') #@DEBUG
#parse_foreclosures_html('/home/jeffschuler/dev/foreclosures/data/20101104-230232/garfield.html') #@DEBUG

#outFilePath = merge_xml_files(curDataDirPath)
#copy_to_site_dir(outFilePath)
logger.debug('DONE!')