#!/usr/bin/python

import urllib2, re, time
import urllib
from urllib import urlencode
from BeautifulSoup import BeautifulSoup
from os import system
from xml.dom.minidom import Document
from datetime import datetime

property_info_fields = ['sale_date', 'sale_num', 'parcel_num', 'location', 'city', 'status', 'prorated_taxes', 'case_num', 'plaintiff', 'defendant', 'address', 'description', 'appraisal', 'minimum_bid', 'sold_amount', 'purchaser', 'attorney']

def parse_info_table(infoTable):
    property_info = {}
    s = infoTable.contents[2].find('p')
    property_info['sale_date'] = s.contents[0]
    #print property_info['sale_date']
    s = s.findNext('p')
    property_info['sale_num'] = s.contents[0]
    #print property_info['sale_num']
    s = s.findNext('input')
    property_info['parcel_num'] = s['value']
    #print property_info['parcel_num']
    s = s.findNext('p')
    property_info['location'] = s.contents[0]
    property_info['city'] = re.sub(' ..st of River', '', s.contents[0])
    #print property_info['city']
    s = s.findNext('p')
    property_info['status'] = re.sub('Status: ', '', s.contents[0])
    property_info['status'] = re.sub('To Be Sold on .*', 'To Be Sold', property_info['status'])
    property_info['status'] = re.sub('SOLD', 'Sold', property_info['status'])
    #print property_info['status']
    s = s.findNext('p')
    property_info['prorated_taxes'] = re.sub('Prorated Taxes: \$', '', s.contents[0])
    #print property_info['prorated_taxes']
    return property_info

def parse_details_table(detailsTable):
    property_info = {}
    s = detailsTable.find('p')
    s = s.findNext('p')
    property_info['case_num'] = s.contents[0]
    #print property_info['case_num']
    s = s.findNext('p')
    s = s.findNext('p')
    property_info['plaintiff'] = s.contents[0]
    #print property_info['plaintiff']
    s = s.findNext('p')
    s = s.findNext('p')
    property_info['defendant'] = s.contents[0]
    #print property_info['defendant']
    s = s.findNext('p')
    s = s.findNext('p')
    property_info['address'] = re.sub('  $', '', s.contents[0])
    #print property_info['address']
    s = s.findNext('p')
    s = s.findNext('p')
    property_info['description'] = s.contents[0]
    #print property_info['description']
    s = s.findNext('p')
    if (s.contents[0] == 'Sold Amount'):
        s = s.findNext('p')
        property_info['sold_amount'] = re.sub('\$', '', s.contents[0])
        #print property_info['sold_amount']
        s = s.findNext('p')
        s = s.findNext('p')
        property_info['purchaser'] = s.contents[0]
        #print property_info['purchaser']
    elif (s.contents[0] == 'Appraisal'):
        s = s.findNext('p')
        property_info['appraisal'] = re.sub('\$', '', s.contents[0])
        #print property_info['appraisal']
        s = s.findNext('p')
        s = s.findNext('p')
        property_info['minimum_bid'] = re.sub('\$ ', '', s.contents[0])
        #print property_info['minimum_bid']
    else:
        s = s.findNext('p')
    s = s.findNext('p')
    s = s.findNext('p')
    if (isinstance(s.contents, (list, tuple)) and len(s.contents) > 0):
        property_info['attorney'] = s.contents[0]
        #print property_info['attorney']
    return property_info

def get_areas_list():
    url = "http://sheriff.cuyahogacounty.us/propertysearch.asp"

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

def output_xml_file(xml_doc):
    datetimeStr = datetime.now().strftime("%Y%m%d-%H%M%S")
    outFileName = 'properties_cleve_west_' + datetimeStr + '.xml'
    outFilePath = '/home/jeffschuler/dev/foreclosures/data_output/' + outFileName
    outFile = file(outFilePath, 'w')
    outFile.write(xml_doc.toprettyxml(indent=""))
    outFile.close() 

# options in <select name="city">

# submit form for each location
#formValues = {
#    "Cleveland West of River"
#}

# http://sheriff.cuyahogacounty.us/foreclosure_city.asp

#formData = urllib.urlencode(formValues)
#formRequest = urllib2.Request('http://....', formData)
#formRequestResponse = urllib2.urlopen(formRequest)
#propertiesHtml = formRequestResponse.read()

foreclosuresHtmlFilePath = '/home/jeffschuler/dev/foreclosures/data_input/foreclosure_city.asp-2010-10-17.html'

## after each
##   <table width="577px" cellpadding="2px" class="info">
## we must add a <tr> for proper parsing:
#replaceInFilesScript = '/home/jeffschuler/bin/replace_in_files.sh'
#findLine = '\"<table width=\\"577px\\" cellpadding=\\"2px\\" class=\\"info\\">\"'
#replaceLine = '\"<table width=\\"577px\\" cellpadding=\\"2px\\" class=\\"info\\"><tr>\"'
#replaceCommandStr = replaceInFilesScript + ' ' + foreclosuresFile + ' ' + findLine + ' ' + replaceLine
##print replaceCommandStr
#system(replaceCommandStr)

xml_doc = parse_foreclosures_html(foreclosuresHtmlFilePath)

output_xml_file(xml_doc)