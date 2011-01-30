#!/usr/bin/python

import sys
import getopt
import re
from datetime import datetime
#import shutil
from os import rename
import os

def usage():
    print "Usage: " + sys.argv[0] + " [-h|--help] -f <file> -d <datestamp ('YYYYMMDD-HHMMSS')>"
    print "Attribute 'date_scraped=\"<datestamp>\"' will be added to the 'properties' XML element in <file>."

def do_replace(xml_file_path, date_time):
    # @TODO: exit with error if xml_file_path doesn't exist
    replacement_str='<properties date_scraped="' + date_time.isoformat() + '">'
    #line = '<properties>\n'
    p = re.compile('<properties>')
    orig_file = open(xml_file_path, "r")
    temp_file_path = xml_file_path + '~'
    temp_file = open(temp_file_path, "w")
    line_num = 0
    num_replacements = 0
    for line in orig_file:
        line_num = line_num + 1
        if line_num < 5 and num_replacements < 1: # @TODO: make this smarter
            (line, num_replacements) = p.subn(replacement_str, line)
        temp_file.write(line)
    temp_file.close()
    orig_file.close()
    # @TODO: test for success
    os.rename(temp_file_path, xml_file_path)

def convert_datestamp(custom_datestamp):
    # convert from YYYYMMDD-HHMMSS (ex. 20101207-054102) to ISO date
    # @TODO: exit with error if datetime is not YYYYMMDD-HHMMSS
    
    #date_time = datetime.strptime(custom_datestamp, "%Y%m%d-%H%M%S") # only in Python >=2.5
    p = re.match(r'(\d\d\d\d)(\d\d)(\d\d)-(\d\d)(\d\d)(\d\d)', custom_datestamp)
    if p.group(0):
        date_time = datetime(int(p.group(1)), int(p.group(2)), int(p.group(3)), int(p.group(4)), int(p.group(5)), int(p.group(6)))
        return date_time

def main(argv):
    # Global cmd-line parameter -based variables
    global _xml_file_path
    _xml_file_path = ''
    global _deploy
    _datestamp = ''

    try:                                
        opts, args = getopt.getopt(argv, "hf:d:", ["help", "file", "datestamp"])
    except getopt.GetoptError:          
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(2)
        elif opt in ("-f", "--file"): 
            _xml_file_path = arg
        elif opt in ("-d", "--datestamp"): 
            _datestamp = arg
    
    # @TODO: exit with error if file or datestamp is not specified
    if _xml_file_path == '' or _datestamp == '':
        usage()
        sys.exit(2)
    
    date_time = convert_datestamp(_datestamp)
    do_replace(_xml_file_path, date_time)

if __name__ == "__main__":
    main(sys.argv[1:])