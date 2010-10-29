#!/usr/bin/python

import urllib2, re, time
import urllib
from urllib import urlencode
from BeautifulSoup import BeautifulSoup
from os import system
from xml.dom.minidom import Document

property_info_fields = ['sale_date', 'sale_number', 'parcel_number', 'location', 'status', 'prorated_taxes', 'case_number', 'plaintiff', 'defendant', 'address', 'description', 'sold_amount', 'purchaser', 'attorney']

def parse_info_table(infoTable):
    property_info = {}
    s = infoTable.contents[2].find('p')
    property_info['sale_date'] = s.contents[0]
    s = s.findNext('p')
    property_info['sale_number'] = s.contents[0]
    s = s.findNext('input')
    property_info['parcel_number'] = s['value']
    s = s.findNext('p')
    property_info['location'] = s.contents[0]
    s = s.findNext('p')
    property_info['status'] = re.sub('Status: ', '', s.contents[0])    
    s = s.findNext('p')
    property_info['prorated_taxes'] = re.sub('Prorated Taxes: \$', '', s.contents[0])
    return property_info

def parse_details_table(detailsTable):
    property_info = {}
    s = detailsTable.find('p')
    s = s.findNext('p')
    property_info['case_number'] = s.contents[0]
    s = s.findNext('p')
    s = s.findNext('p')
    property_info['plaintiff'] = s.contents[0]
    s = s.findNext('p')
    s = s.findNext('p')
    property_info['defendant'] = s.contents[0]
    s = s.findNext('p')
    s = s.findNext('p')
    property_info['address'] = re.sub('  $', '', s.contents[0])
    s = s.findNext('p')
    s = s.findNext('p')
    property_info['description'] = s.contents[0]
    s = s.findNext('p')
    if (s.contents[0] == 'Sold Amount'):
        s = s.findNext('p')
        property_info['sold_amount'] = re.sub('\$', '', s.contents[0])
        s = s.findNext('p')
        s = s.findNext('p')
        property_info['purchaser'] = s.contents[0]
    else:
        s = s.findNext('p')
    s = s.findNext('p')
    s = s.findNext('p')
    property_info['attorney'] = s.contents[0]
    
    return property_info

# get each location
# http://sheriff.cuyahogacounty.us/propertysearch.asp
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

foreclosuresFile = '/home/jeffschuler/dev/foreclosures/data/foreclosure_city.asp-2010-10-17.html'

## after each
##   <table width="577px" cellpadding="2px" class="info">
## we must add a <tr> for proper parsing:
#replaceInFilesScript = '/home/jeffschuler/bin/replace_in_files.sh'
#findLine = '\"<table width=\\"577px\\" cellpadding=\\"2px\\" class=\\"info\\">\"'
#replaceLine = '\"<table width=\\"577px\\" cellpadding=\\"2px\\" class=\\"info\\"><tr>\"'
#replaceCommandStr = replaceInFilesScript + ' ' + foreclosuresFile + ' ' + findLine + ' ' + replaceLine
##print replaceCommandStr
#system(replaceCommandStr)

foreclosuresHtml = file(foreclosuresFile, 'r')

xml_doc = Document()
xml_properties = xml_doc.createElement("properties")
xml_doc.appendChild(xml_properties)

soup = BeautifulSoup(foreclosuresHtml)
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

print xml_doc.toprettyxml(indent="  ")