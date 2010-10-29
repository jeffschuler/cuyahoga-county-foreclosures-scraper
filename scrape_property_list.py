#!/usr/bin/python

import urllib2, re, time
import urllib
from urllib import urlencode
from BeautifulSoup import BeautifulSoup
from os import system

def parse_info_table(infoTable):
    prop_info = {}
    s = infoTable.contents[2].find('p')
    prop_info['sale_date'] = s.contents[0]
    s = s.findNext('p')
    prop_info['sale_number'] = s.contents[0]
    s = s.findNext('input')
    prop_info['parcel_number'] = s['value']
    s = s.findNext('p')
    prop_info['location'] = s.contents[0]
    s = s.findNext('p')
    prop_info['status'] = re.sub('Status: ', '', s.contents[0])    
    s = s.findNext('p')
    prop_info['prorated_taxes'] = re.sub('Prorated Taxes: \$', '', s.contents[0])
    return prop_info

def parse_details_table(detailsTable):
    prop_info = {}
    s = detailsTable.find('p')
    s = s.findNext('p')
    prop_info['case_number'] = s.contents[0]
    s = s.findNext('p')
    s = s.findNext('p')
    prop_info['plaintiff'] = s.contents[0]
    s = s.findNext('p')
    s = s.findNext('p')
    prop_info['defendant'] = s.contents[0]
    s = s.findNext('p')
    s = s.findNext('p')
    prop_info['address'] = re.sub('  $', '', s.contents[0])
    s = s.findNext('p')
    s = s.findNext('p')
    prop_info['description'] = s.contents[0]
    s = s.findNext('p')
    if (s.contents[0] == 'Sold Amount'):
        s = s.findNext('p')
        prop_info['sold_amount'] = re.sub('\$', '', s.contents[0])
        s = s.findNext('p')
        s = s.findNext('p')
        prop_info['purchaser'] = s.contents[0]
    else:
        s = s.findNext('p')
    s = s.findNext('p')
    s = s.findNext('p')
    prop_info['attorney'] = s.contents[0]
    
    return prop_info

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

foreclosuresFile = '/home/jeffschuler/dev/foreclosures/foreclosure_city.asp-2010-10-17-abbrev.html'

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

soup = BeautifulSoup(foreclosuresHtml)
#print soup.prettify()

#soup.findAll('table', width="577px")
#soup.find('table', width="577px")

infoTable = soup.find("table", "info")
while infoTable:
    detailsTable = infoTable.findNextSibling('table', "detail")
    prop_info = parse_info_table(infoTable)
    details = parse_details_table(detailsTable)
    prop_info.update(details)
    print prop_info
    infoTable = detailsTable.findNextSibling("table", "info")

#class="detail"
#class="info"