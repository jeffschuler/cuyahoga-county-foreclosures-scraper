#!/usr/bin/python

# Shell
import sys
import getopt

# Fetching
import urllib2
import urllib
import cookielib

# Parsing
import string
import re
from bs4 import BeautifulSoup

# Debug
import logging
import logging.handlers
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


# Run live search or use pre-saved data
global _LIVE_MODE
_LIVE_MODE = False


# Output data
global _OUTPUT_DIR
_OUTPUT_DIR = 'data'


def run_parcel_search(parcel_num):
    """Submit form to search for a single parcel number, and return response."""

    _logger.debug('getting parcel #' + parcel_num)

    base_url = 'http://sheriff.cuyahogacounty.us/en-US'
    page_url = base_url + '/Foreclosure-Property-Search.aspx'
    form_url = base_url + '/PropertySearch.aspx?LanguageCD=en-US&ItemKey=26945&pb=y'

    # establish cookies
    jar = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
    urllib2.install_opener(opener)
    opener.open(page_url)
    #pp.pprint(jar)

    # @TODO: scrape __EVENTVALIDATION and __VIEWSTATE from page

    form_values = {
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
        '__EVENTVALIDATION': '/wEWRQKHwZ8qAvCK/osPArrInd8NArv607MCAsmmlswJApKKt8IKApzF8MkBApDYh4oLApCtvu0MAvOM24wDAt2cjucFAobAtdYJAqWBuMMBAoal6q8IAoWOhpgIApjvoeAJAv/E7YIMAqfN9ZIHAoXriYoDAtDgyOoFAvHl0v4KAuCL6I0OAtDY+2wC6JacoQcCg5q7xQwCtcKosAECksaSNgKb8MOwBwKC976eCwKg34o9Av261ZkKAsCepY8IAtPy9+wJArXpsdsGAtT8t5kCAovgsaIJArvo6OMOAov/nv0JAtSRsJIBArbnlrAEAuKYmpMPApr7jYwDAt29uYIEAsq1vbUGAqO1uPAKAuncyLEDAryMr4ALApC7t4sDAvzrlsYPAuHA6LYCAvTI6uQMAruT75sDAp6P+7EHAs7dx80OAtLm76IKAo7f7X0C9YatlAUCt+yS4wsCl9/mpgUC4MCigAsCwLeF/gMClPiw8QICl4Dj/QkCk5D+7AYC6sOdzwkCw6mmgQQCztybiAUC/fSHhg8Cqu6vzAtcl1wrlc6RGKJQZ6jXSYTaZxVjow==',
        '__VIEWSTATE': '/wEPDwUKLTk4MjE4NjM3Ng9kFgJmD2QWAgIDD2QWDAIHDw8WBB4ISW1hZ2VVcmwFIS9pbWdfc2hlcmlmZi9lbi1VUy9zaXRlX3RpdGxlLmpwZx4NQWx0ZXJuYXRlVGV4dAUPQ3V5YWhvZ2EgQ291bnR5ZGQCCQ9kFgJmD2QWBgIBDw8WBh4IQ3NzQ2xhc3NlHgVXaWR0aBsAAAAAAOBlQAEAAAAeBF8hU0ICggIWBB4Hb25DbGljawU2Z2V0RWxlbWVudEJ5SWQoJ2N0bDAwX1NpdGVTZWFyY2gxX3R4dFRlcm1zJykudmFsdWU9Jyc7HgNhbHRlZAIDDw8WCB4EVGV4dAUGU2VhcmNoHg1PbkNsaWVudENsaWNrBWBpZihjdGwwMF9TaXRlU2VhcmNoMV90eHRUZXJtcy52YWx1ZSA9PScnIHx8IGN0bDAwX1NpdGVTZWFyY2gxX3R4dFRlcm1zLnZhbHVlID09JycpIHJldHVybiBmYWxzZTsfAgUMc2VhcmNoQnV0dG9uHwQCAmRkAgUPDxYCHwgFYGlmKGN0bDAwX1NpdGVTZWFyY2gxX3R4dFRlcm1zLnZhbHVlID09JycgfHwgY3RsMDBfU2l0ZVNlYXJjaDFfdHh0VGVybXMudmFsdWUgPT0nJykgcmV0dXJuIGZhbHNlO2RkAg0QPCsACQIADxYEHg1OZXZlckV4cGFuZGVkZB4LXyFEYXRhQm91bmRnZAgUKwAPBTswOjAsMDoxLDA6MiwwOjMsMDo0LDA6NSwwOjYsMDo3LDA6OCwwOjksMDoxMCwwOjExLDA6MTIsMDoxMxQrAAIWCB8HBQRIb21lHgtOYXZpZ2F0ZVVybAUwaHR0cDovL3NoZXJpZmYuY3V5YWhvZ2Fjb3VudHkudXMvZW4tVVMvaG9tZS5hc3B4HghEYXRhUGF0aAUFLTk5OTkeCURhdGFCb3VuZGdkFCsAAhYIHwcFE0dlbmVyYWwgSW5mb3JtYXRpb24fCwU/aHR0cDovL3NoZXJpZmYuY3V5YWhvZ2Fjb3VudHkudXMvZW4tVVMvZ2VuZXJhbC1pbmZvcm1hdGlvbi5hc3B4HwwFBjEzOTQ5Mh8NZxQrAAoFIzA6MCwwOjEsMDoyLDA6MywwOjQsMDo1LDA6NiwwOjcsMDo4FCsAAhYIHwcFDkNhc2UgRmxvd2NoYXJ0HwsFOmh0dHA6Ly9zaGVyaWZmLmN1eWFob2dhY291bnR5LnVzL2VuLVVTL2Nhc2UtZmxvd2NoYXJ0LmFzcHgfDAUFNzk1ODYfDWdkFCsAAhYIHwcFDkNpdmlsIERpdmlzaW9uHwsFOmh0dHA6Ly9zaGVyaWZmLmN1eWFob2dhY291bnR5LnVzL2VuLVVTL2NpdmlsLWRpdmlzaW9uLmFzcHgfDAUFNzk1OTgfDWdkFCsAAhYIHwcFG0NvbmNlYWxlZCBDYXJyeSBJbmZvcm1hdGlvbh8LBUdodHRwOi8vc2hlcmlmZi5jdXlhaG9nYWNvdW50eS51cy9lbi1VUy9Db25jZWFsZWQtQ2FycnktSW5mb3JtYXRpb24uYXNweB8MBQYxNDgwMDcfDWdkFCsAAhYIHwcFEUJhY2tncm91bmQgQ2hlY2tzHwsFPWh0dHA6Ly9zaGVyaWZmLmN1eWFob2dhY291bnR5LnVzL2VuLVVTL2JhY2tncm91bmQtY2hlY2tzLmFzcHgfDAUGMTQ3NTczHw1nZBQrAAIWCB8HBQpDb250YWN0IFVzHwsFQmh0dHA6Ly9zaGVyaWZmLmN1eWFob2dhY291bnR5LnVzL2VuLVVTL1NZTi8yNjkxNC9QYWdlVGVtcGxhdGUuYXNweB8MBQU3OTYwNR8NZ2QUKwACFggfBwUSRXhwbG9yZXJzIFBvc3QgNzAxHwsFPmh0dHA6Ly9zaGVyaWZmLmN1eWFob2dhY291bnR5LnVzL2VuLVVTL2V4cGxvcmVycy1wb3N0LTcwMS5hc3B4HwwFBTc5NjA2Hw1nZBQrAAIWCB8HBQxTdWJtaXQgYSBUaXAfCwU2aHR0cDovL3NoZXJpZmYuY3V5YWhvZ2Fjb3VudHkudXMvZW4tVVMvc3VibWl0LXRpcC5hc3B4HwwFBTc5NjA3Hw1nZBQrAAIWCB8HBRRPcmdhbml6YXRpb25hbCBDaGFydB8LBUBodHRwOi8vc2hlcmlmZi5jdXlhaG9nYWNvdW50eS51cy9lbi1VUy9Pcmdhbml6YXRpb25hbC1DaGFydC5hc3B4HwwFBTc5NjA4Hw1nZBQrAAIWCB8HBQRWSU5FHwsFWWh0dHA6Ly9zaGVyaWZmLmN1eWFob2dhY291bnR5LnVzL2VuLVVTL1ZpY3RpbS1JbmZvcm1hdGlvbi1Ob3RpZmljYXRpb24tRXZlcnlkYXktVklORS5hc3B4HwwFBTc5NjA5Hw1nZBQrAAIWCB8HBQtDb3JyZWN0aW9ucx8LBTdodHRwOi8vc2hlcmlmZi5jdXlhaG9nYWNvdW50eS51cy9lbi1VUy9jb3JyZWN0aW9ucy5hc3B4HwwFBjEzMTgwMh8NZxQrAAQFCzA6MCwwOjEsMDoyFCsAAhYIHwcFEkNvcnJlY3Rpb25zIENlbnRlch8LBU5odHRwOi8vc2hlcmlmZi5jdXlhaG9nYWNvdW50eS51cy9lbi1VUy9DdXlhaG9nYS1Db3VudHktQ29ycmVjdGlvbnMtQ2VudGVyLmFzcHgfDAUFNzk2MTcfDWdkFCsAAhYIHwcFEklubWF0ZSBJbmZvcm1hdGlvbh8LBT5odHRwOi8vc2hlcmlmZi5jdXlhaG9nYWNvdW50eS51cy9lbi1VUy9pbm1hdGUtaW5mb3JtYXRpb24uYXNweB8MBQU3OTYxOR8NZ2QUKwACFggfBwUdUmVnaXN0cmF0aW9uICZhbXA7IFZpc2l0YXRpb24fCwVDaHR0cDovL3NoZXJpZmYuY3V5YWhvZ2Fjb3VudHkudXMvZW4tVVMvcmVnaXN0cmF0aW9uLXZpc2l0YXRpb24uYXNweB8MBQYxNDEyNTMfDWdkFCsAAhYIHwcFEUZvcmVjbG9zdXJlIFNhbGVzHwsFPWh0dHA6Ly9zaGVyaWZmLmN1eWFob2dhY291bnR5LnVzL2VuLVVTL0ZvcmVjbG9zdXJlLVNhbGVzLmFzcHgfDAUGMTMyNTI1Hw1nFCsABgUTMDowLDA6MSwwOjIsMDozLDA6NBQrAAIWCB8HBQ5UZXJtcyBvZiBTYWxlcx8LBTdodHRwOi8vc2hlcmlmZi5jdXlhaG9nYWNvdW50eS51cy9lbi1VUy9UZXJtcy1TYWxlcy5hc3B4HwwFBjEzMjMwMR8NZ2QUKwACFggfBwULRllJIFdhcm5pbmcfCwU3aHR0cDovL3NoZXJpZmYuY3V5YWhvZ2Fjb3VudHkudXMvZW4tVVMvRllJLVdhcm5pbmcuYXNweB8MBQU3OTYzNR8NZ2QUKwACFggfBwUPU2FsZXMgQnVsbGV0aW5zHwsFR2h0dHA6Ly9zaGVyaWZmLmN1eWFob2dhY291bnR5LnVzL2VuLVVTL0ZvcmVjbG9zdXJlLVNhbGVzLUJ1bGxldGlucy5hc3B4HwwFBjEzMjMwMh8NZ2QUKwACFggfBwUPUHJvcGVydHkgU2VhcmNoHwsFR2h0dHA6Ly9zaGVyaWZmLmN1eWFob2dhY291bnR5LnVzL2VuLVVTL0ZvcmVjbG9zdXJlLVByb3BlcnR5LVNlYXJjaC5hc3B4HwwFBjEzMjUyNB8NZ2QUKwACFggfBwUPVW5jbGFpbWVkIEZ1bmRzHwsFO2h0dHA6Ly9zaGVyaWZmLmN1eWFob2dhY291bnR5LnVzL2VuLVVTL1VuY2xhaW1lZC1GdW5kcy5hc3B4HwwFBjEzNTQyNB8NZ2QUKwACFggfBwUPTGF3IEVuZm9yY2VtZW50HwsFO2h0dHA6Ly9zaGVyaWZmLmN1eWFob2dhY291bnR5LnVzL2VuLVVTL0xhdy1FbmZvcmNlbWVudC5hc3B4HwwFBTc5NjUwHw1nFCsACQUfMDowLDA6MSwwOjIsMDozLDA6NCwwOjUsMDo2LDA6NxQrAAIWCB8HBRdBcHByZWhlbnNpb24gVW5pdCAoSVNQKR8LBT1odHRwOi8vc2hlcmlmZi5jdXlhaG9nYWNvdW50eS51cy9lbi1VUy9BcHByZWhlbnNpb24tVW5pdC5hc3B4HwwFBTc5NjUxHw1nZBQrAAIWCB8HBRBDcmltaW5hbCBSZWNvcmRzHwsFPGh0dHA6Ly9zaGVyaWZmLmN1eWFob2dhY291bnR5LnVzL2VuLVVTL0NyaW1pbmFsLVJlY29yZHMuYXNweB8MBQU3OTY1Mh8NZ2QUKwACFggfBwUQRGV0ZWN0aXZlIEJ1cmVhdR8LBTxodHRwOi8vc2hlcmlmZi5jdXlhaG9nYWNvdW50eS51cy9lbi1VUy9EZXRlY3RpdmUtQnVyZWF1LmFzcHgfDAUFNzk2NTMfDWdkFCsAAhYIHwcFDkhvbWUgRGV0ZW50aW9uHwsFOmh0dHA6Ly9zaGVyaWZmLmN1eWFob2dhY291bnR5LnVzL2VuLVVTL0hvbWUtRGV0ZW50aW9uLmFzcHgfDAUFNzk2NTQfDWdkFCsAAhYIHwcFB0s5IFVuaXQfCwUzaHR0cDovL3NoZXJpZmYuY3V5YWhvZ2Fjb3VudHkudXMvZW4tVVMvSzktVW5pdC5hc3B4HwwFBjExMzgwOB8NZ2QUKwACFggfBwUJTmFyY290aWNzHwsFNWh0dHA6Ly9zaGVyaWZmLmN1eWFob2dhY291bnR5LnVzL2VuLVVTL25hcmNvdGljcy5hc3B4HwwFBjEzMDIzMx8NZxQrAAIFAzA6MBQrAAIWCB8HBSJDb25maWRlbnRpYWwgTmFyY290aWNzIFJlcG9ydCBGb3JtHwsFTmh0dHA6Ly9zaGVyaWZmLmN1eWFob2dhY291bnR5LnVzL2VuLVVTL0NvbmZpZGVudGlhbC1OYXJjb3RpY3MtUmVwb3J0LUZvcm0uYXNweB8MBQYxMjc2NjUfDWdkFCsAAhYIHwcFCVNPUk4gVW5pdB8LBUBodHRwOi8vc2hlcmlmZi5jdXlhaG9nYWNvdW50eS51cy9lbi1VUy9TZXh1YWwtT2ZmZW5kZXItVW5pdC5hc3B4HwwFBjEyOTkxNB8NZxQrAAIFAzA6MBQrAAIWCB8HBRJTZXggT2ZmZW5kZXIgVGllcnMfCwU+aHR0cDovL3NoZXJpZmYuY3V5YWhvZ2Fjb3VudHkudXMvZW4tVVMvc2V4LW9mZmVuZGVyLXRpZXJzLmFzcHgfDAUFNzk2NjQfDWdkFCsAAhYIHwcFF0Fyc29uIE9mZmVuZGVyIFJlZ2lzdHJ5HwsFQ2h0dHA6Ly9zaGVyaWZmLmN1eWFob2dhY291bnR5LnVzL2VuLVVTL2Fyc29uLW9mZmVuZGVyLXJlZ2lzdHJ5LmFzcHgfDAUGMTQ4NDgzHw1nZBQrAAIWCB8HBRNQcm90ZWN0aXZlIFNlcnZpY2VzHwsFR2h0dHA6Ly9zaGVyaWZmLmN1eWFob2dhY291bnR5LnVzL2VuLVVTL1Byb3RlY3RpdmVTZXJ2aWNlcy0vc2hlcmlmZi5hc3B4HwwFBjExNjMyMh8NZxQrAAMFBzA6MCwwOjEUKwACFggfBwUWRW1lcmdlbmN5IENvbnRhY3QgSW5mbx8LBUNodHRwOi8vc2hlcmlmZi5jdXlhaG9nYWNvdW50eS51cy9lbi1VUy9QUy1FbWVyZ2VuY3lDb250YWN0SW5mby5hc3B4HwwFBTc5Njk3Hw1nZBQrAAIWCB8HBQVGQVEncx8LBTBodHRwOi8vc2hlcmlmZi5jdXlhaG9nYWNvdW50eS51cy9lbi1VUy9GQVFzLmFzcHgfDAUFNzk2OTgfDWdkFCsAAhYIHwcFCENhbGVuZGFyHwsFNGh0dHA6Ly9zaGVyaWZmLmN1eWFob2dhY291bnR5LnVzL2VuLVVTL2NhbGVuZGFyLmFzcHgfDAUFNzk2NjYfDWdkFCsAAhYIHwcFGkZyZXF1ZW50bHkgQXNrZWQgUXVlc3Rpb25zHwsFRmh0dHA6Ly9zaGVyaWZmLmN1eWFob2dhY291bnR5LnVzL2VuLVVTL0ZyZXF1ZW50bHktQXNrZWQtUXVlc3Rpb25zLmFzcHgfDAUFNzk1ODcfDWcUKwAEBQswOjAsMDoxLDA6MhQrAAIWCB8HBTlDaXZpbCBEaXZpc2lvbiAtIEZvcmVjbG9zdXJlIFNhbGVzLCBTdWJwb2VuYXMgJmFtcDsgV3JpdHMfCwVQaHR0cDovL3NoZXJpZmYuY3V5YWhvZ2Fjb3VudHkudXMvZW4tVVMvRkFRLUNpdmlsLURpdmlzaW9uLUZvcmVjbG9zdXJlLVNhbGVzLmFzcHgfDAUFNzk1ODkfDWdkFCsAAhYIHwcFIENoaWxkcmVuIE5lZWQgU3VwcG9ydCBUYXNrIEZvcmNlHwsFUGh0dHA6Ly9zaGVyaWZmLmN1eWFob2dhY291bnR5LnVzL2VuLVVTL0ZBUS1DaGlsZHJlbi1OZWVkLVN1cHBvcnQtVGFzay1Gb3JjZS5hc3B4HwwFBTc5NTk2Hw1nZBQrAAIWCB8HBS9TZXggT2ZmZW5kZXIgUmVnaXN0cmF0aW9uIGFuZCBOb3RpZmljYXRpb24gVW5pdB8LBVtodHRwOi8vc2hlcmlmZi5jdXlhaG9nYWNvdW50eS51cy9lbi1VUy9GQVEtU2V4LU9mZmVuZGVyLVJlZ2lzdHJhdGlvbi1Ob3RpZmljYXRpb24tVW5pdC5hc3B4HwwFBTc5NTk3Hw1nZBQrAAIWCB8HBQVMaW5rcx8LBTFodHRwOi8vc2hlcmlmZi5jdXlhaG9nYWNvdW50eS51cy9lbi1VUy9saW5rcy5hc3B4HwwFBTc5NjExHw1nFCsAAwUHMDowLDA6MRQrAAIWCB8HBRxDb21tdW5pdHkgUG9saWNlIERlcGFydG1lbnRzHwsFWGh0dHA6Ly9zaGVyaWZmLmN1eWFob2dhY291bnR5LnVzL2VuLVVTL0N1eWFob2dhLUNvdW50eS1Db21tdW5pdHktUG9saWNlLURlcGFydG1lbnRzLmFzcHgfDAUFNzk2NjcfDWdkFCsAAhYIHwcFFE9oaW8gQ291bnR5IFNoZXJpZmZzHwsFQGh0dHA6Ly9zaGVyaWZmLmN1eWFob2dhY291bnR5LnVzL2VuLVVTL09oaW8tQ291bnR5LVNoZXJpZmZzLmFzcHgfDAUFNzk2MTUfDWdkFCsAAhYIHwcFGFJ4IERydWcgRHJvcCBCb3ggUHJvZ3JhbR8LBUBodHRwOi8vc2hlcmlmZi5jdXlhaG9nYWNvdW50eS51cy9lbi1VUy9SeERydWdEcm9wQm94UHJvZ3JhbS5hc3B4HwwFBjE0NTY5MR8NZ2QUKwACFggfBwUOUHJlc3MgUmVsZWFzZXMfCwU6aHR0cDovL3NoZXJpZmYuY3V5YWhvZ2Fjb3VudHkudXMvZW4tVVMvcHJlc3MtcmVsZWFzZXMuYXNweB8MBQYxMzE2OTAfDWdkFCsAAhYIHwcFBUZvcm1zHwsFMWh0dHA6Ly9zaGVyaWZmLmN1eWFob2dhY291bnR5LnVzL2VuLVVTL2Zvcm1zLmFzcHgfDAUGMTQzMTQxHw1nZBQrAAIWCB8HBQhTaXRlIG1hcB8LBTNodHRwOi8vc2hlcmlmZi5jdXlhaG9nYWNvdW50eS51cy9lbi1VUy9TaXRlTWFwLmFzcHgfDAUFNzk1NDAfDWdkFCsAAhYIHwcFCkNvbnRhY3QgVXMfCwU1aHR0cDovL3NoZXJpZmYuY3V5YWhvZ2Fjb3VudHkudXMvZW4tVVMvQ29udGFjdFVzLmFzcHgfDAUFNzk1NTYfDWdkBRNjdGwwMCRjdGwxMXxubm5ubm5uZAIVD2QWAmYPDxYCHwcF+wI8YSBjbGFzcz0nQnJlYWRDcnVtYkxpbmsnIGhyZWY9J2h0dHA6Ly9zaGVyaWZmLmN1eWFob2dhY291bnR5LnVzL2VuLVVTL2hvbWUuYXNweCc+SG9tZTwvYT4mbmJzcDs8c3BhbiBjbGFzcz0nQnJlYWRDcnVtYlNlcGFyYXRvcic+Jmd0Ozwvc3Bhbj4mbmJzcDs8YSBjbGFzcz0nQnJlYWRDcnVtYkxpbmsnIGhyZWY9J2h0dHA6Ly9zaGVyaWZmLmN1eWFob2dhY291bnR5LnVzL2VuLVVTL0ZvcmVjbG9zdXJlLVNhbGVzLmFzcHgnPkZvcmVjbG9zdXJlIFNhbGVzPC9hPiZuYnNwOzxzcGFuIGNsYXNzPSdCcmVhZENydW1iU2VwYXJhdG9yJz4mZ3Q7PC9zcGFuPiZuYnNwOzxzcGFuIGNsYXNzPSdCcmVhZENydW1iQ3VycmVudFBhZ2UgJz5Qcm9wZXJ0eSBTZWFyY2g8L3NwYW4+ZGQCFw9kFgICAQ9kFgJmD2QWDAIBDxYCHwcFD1Byb3BlcnR5IFNlYXJjaGQCAw8WAh8HBcIBPGJyIC8+CjxiciAvPgo8YmxvY2txdW90ZT48c3BhbiBzdHlsZT0iY29sb3I6ICNmZjAwMDA7Ij48c3Ryb25nPk5PVEU6PC9zdHJvbmc+IEFzIG9mIE5vdmVtYmVyIDUsIDIwMTIsIHRoZSB0aW1lIG9mIHRoZSBGb3JlY2xvc3VyZSBTYWxlcyB3aWxsIGJlIG1vdmVkIHRvIDk6MDBhbSA8L3NwYW4+PC9ibG9ja3F1b3RlPjxiciAvPgo8YnIgLz5kAgUPDxYCHglNYXhMZW5ndGhmZGQCCQ8WGh4RQ3VsdHVyZURhdGVGb3JtYXQFA01EWR4bQ3VsdHVyZVRob3VzYW5kc1BsYWNlaG9sZGVyBQEsHgtDdWx0dXJlTmFtZQUFZW4tVVMeFkN1bHR1cmVEYXRlUGxhY2Vob2xkZXIFAS8eDERpc3BsYXlNb25leQsphgFBamF4Q29udHJvbFRvb2xraXQuTWFza2VkRWRpdFNob3dTeW1ib2wsIEFqYXhDb250cm9sVG9vbGtpdCwgVmVyc2lvbj0zLjAuMzA1MTIuMjAzMTUsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49MjhmMDFiMGU4NGI2ZDUzZQAeDkFjY2VwdE5lZ2F0aXZlCysEAB4KQWNjZXB0QW1QbWgeE092ZXJyaWRlUGFnZUN1bHR1cmVoHhlDdWx0dXJlRGVjaW1hbFBsYWNlaG9sZGVyBQEuHhZDdWx0dXJlQU1QTVBsYWNlaG9sZGVyBQVBTTtQTR4gQ3VsdHVyZUN1cnJlbmN5U3ltYm9sUGxhY2Vob2xkZXIFASQeFkN1bHR1cmVUaW1lUGxhY2Vob2xkZXIFAToeDklucHV0RGlyZWN0aW9uCymKAUFqYXhDb250cm9sVG9vbGtpdC5NYXNrZWRFZGl0SW5wdXREaXJlY3Rpb24sIEFqYXhDb250cm9sVG9vbGtpdCwgVmVyc2lvbj0zLjAuMzA1MTIuMjAzMTUsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49MjhmMDFiMGU4NGI2ZDUzZQBkAhcPEA8WBh4ORGF0YVZhbHVlRmllbGQFCWNfQ2l0eVVJRB4NRGF0YVRleHRGaWVsZAUKY19DaXR5TmFtZR8KZ2QQFTsRLSBTZWxlY3QgYSBDaXR5IC0LQmF5IFZpbGxhZ2UJQmVhY2h3b29kB0JlZGZvcmQPQmVkZm9yZCBIZWlnaHRzC0JlbnRsZXl2aWxsBUJlcmVhCUJyYXRlbmFobAtCcmVja3N2aWxsZRFCcm9hZHZpZXcgSGVpZ2h0cwpCcm9vayBQYXJrEEJyb29rbHluIEhlaWdodHMQQnJvb2tseW4gVmlsbGFnZRZDaGFncmluIEZhbGxzIFRvd25zaGlwD0NoYWdyaW4gVmlsbGFnZRdDbGV2ZWxhbmQgRWFzdCBvZiBSaXZlchFDbGV2ZWxhbmQgSGVpZ2h0cxdDbGV2ZWxhbmQgV2VzdCBvZiBSaXZlchBDdXlhaG9nYSBIZWlnaHRzDkVhc3QgQ2xldmVsYW5kBkV1Y2xpZA1GYWlydmlldyBQYXJrCEdBUkZJRUxEEEdhcmZpZWxkIEhlaWdodHMLR2F0ZXMgTWlsbHMKR2xlbndpbGxvdxBIaWdobGFuZCBIZWlnaHRzDkhpZ2hsYW5kIEhpbGxzDkh1bnRpbmcgVmFsbGV5DEluZGVwZW5kZW5jZQhMYWtld29vZAlMeW5kaHVyc3QNTWFwbGUgSGVpZ2h0cxBNYXlmaWVsZCBIZWlnaHRzEE1heWZpZWxkIFZpbGxhZ2USTWlkZGxlYnVyZyBIZWlnaHRzDk1vcmVsYW5kIEhpbGxzEE5ld2J1cmdoIEhlaWdodHMNTm9ydGggT2xtc3RlZA5Ob3J0aCBSb3lhbHRvbgdPYWt3b29kDU9sbXN0ZWQgRmFsbHMQT2xtc3RlZCBUb3duc2hpcAZPcmFuZ2UFUGFybWENUGFybWEgSGVpZ2h0cwtQZXBwZXIgUGlrZRBSaWNobW9uZCBIZWlnaHRzC1JvY2t5IFJpdmVyC1NldmVuIEhpbGxzDlNoYWtlciBIZWlnaHRzBVNvbG9uDFNvdXRoIEV1Y2xpZAxTdHJvbmdzdmlsbGUSVW5pdmVyc2l0eSBIZWlnaHRzC1ZhbGxleSBWaWV3DFdhbHRvbiBIaWxscxRXYXJyZW5zdmlsbGUgSGVpZ2h0cwhXZXN0bGFrZRU7ATAkZGRkMzJhYjMtZmY4NS00Yzk1LTlmZjQtNWUzNTdhZmM1MWRhJGIxZmI1MDM1LThlNjAtNDdmOC1iNTU4LTU5MWM5MGRiZWUxOSQ4MTI0MzFmZi0zZjUyLTRhYTYtYTgzMi1kMTQ3OGRlNTgzZTQkZjFlYmQzMmUtM2NhMy00MTA5LTk1YWMtNjgxOTIxOWVjYjJlJDYwMjdhYjIzLWM4YjAtNDE1ZS04ZDRlLWUwM2JkNzY2YjU5YyQ4ZWY1NGI5NC1hM2I5LTRkZGEtYTgyMi0zNTdiOTQ3ODA1NDYkMmVmOTgyYzMtNTM2NS00MjM3LWFhZDMtYThjOWFlNWVkZjZlJGM5ZWYxNDYxLTRkNjYtNDA5Yi1hYzE4LThhMmUwOThmZTc3YiRkYmM2NTk4Yi0wMDBkLTQ0OWUtYWMxNC1jZTAxMTI1ZGE1NDkkYTZhMGU5MjYtZjgyZS00NmUyLTk2ZjctYmI0MjlhZGNjOTJjJGYxNTYxNjkyLThlNjUtNDc0ZS1hNTJiLWI3NDgzNjgzOWNmMyQ3Yjk3YTc3Ni00MzcyLTRmMWUtYTAyMC0xNjhkNTY3MWYxY2IkY2M5MjY3ZjYtODIzMS00YTQ1LTg1MzItZDFiMDI5ZTRiZjAzJGZkMGY2N2Y2LTMzMWYtNGM0My1hZTEwLTQxNzFkMzE3ODE1YyRiODJmZGE0OC0yMjQxLTQxY2UtODRjNS1iNDAyZDYxZmRkZmUkMmI3ZWJkZjItNzNhMC00YTg5LWFlNmMtYjRkNDI1MDFiMTg4JDk3YjhhZTU1LTBlYjUtNDkzZS1hZjdlLWY0MWIyZWJjMDY1NCRiYzk2ZjZiYy1mOGEwLTQxZmQtODgxYi0xMjk2YWU4NzA2MzIkNDRkNzcwNDgtYTg2OS00NTQ2LTk1NzgtZjdiODIxZWExZjY0JDkwODVlYWEwLTdmYTQtNGFlMi05NzQ1LWJkNDg4MGI4ZDE4NSRhYzk2MGFkNS0zNTA0LTQ0YmYtYmEzOS0wOGFkMzNhYTc0NWYkZWYwZTU5MjktY2M3Zi00OWZjLWFiMDEtMTE1NzlhMjlkMWZhJGJmMDkzNDU1LTNlYWYtNDdmNS1iYWRhLTZlYjNlYTUwZmFkNiRiZGZmOWY2NS00M2FiLTRiOWUtYjFkOC03MTYwMGQ2NjFhYjMkNzY3NTliNWQtODNiZi00ODk4LWE4YWYtMjc0NTc4YTA3OTUwJGQ5MWYzMTQwLWM5ZDgtNDI1Zi05ZTBlLTA1Mjc0NTNiNTQ1OCRiODgxOGEzOS0zODRlLTQ1OGItYWQ3Ni1jOGI5MzYxM2UxNDckZDYzNTI3NGEtOTJjZC00ZDNlLTg4NDUtODgzZmRlN2E2ZTQ5JGZkMzRhNWM4LTQ4Y2YtNDhiMS1iYzgwLTVhNTJlMTNmYzFlOSRiM2UzNjg5MC1jYzdmLTQ5MjUtYTQ0NC0wYzE4M2NmZGQ3OTkkZTYzNzAwMDYtOGQ5Ny00ZTRlLWI5MmMtYjNkYjVkMzFmN2EyJGQ3ZjlkZWY4LTBjZDYtNDg0NC1iMWFhLWJmMzBjNmNhYTI2NCQzYmZiMjg3Yi1lNWZkLTQzZmMtOTA0MS05YmU4ODA2ODk2YmIkYzNmYmUwOGEtODc5Yi00NzgyLWI0M2MtNWRlOGM4YzYyODliJGJlODMzMDY3LWE1N2EtNDAyZS04ODU1LTFhNGM4MTM3YmQzZCQwNGEzZmRkZi05N2E2LTQ1NmItYWQwMy03NTVkMGY4YzE1YjIkYzhlMWVmYTAtZDM3OS00YmE1LTg2MmEtNmMxNTlhZDllMWM4JGQ3MGQyNTgyLWQ3NGQtNDkxMi04NjVmLWFmZTIzMWQ4NzVjOSQxOTQ5ZmQ2OS1kOGZhLTQwMzAtYjMxOS0wODdlNzZiMTJiZTIkMDQzMWVkNTEtMWQ5Zi00ODYzLWI5OGQtM2MzMGZjOWJhOGY1JGE5NGU5ZTY0LWQ1ODItNGYzNS05OTdhLWMxYWJkYjMwYzc1MSRjMDU2MTk5NC01NWJkLTRkYTAtOTcxMi01ZjI5YzJkNzZhMDckNzJhNTljOTctZTViMi00ZGQ0LThjMDYtM2NlYWQ1ZDc4ZGFiJDllZmVhMTQwLWE5YTQtNGE5Mi1iODQ2LWE1NWMzMWFhYzVhYiQ0MzE2MWI4Ni0xNWUzLTRlYTUtODZhMy0zYzU5OTRiZDU2YWYkOWM1MDFlZDAtOTY5My00ZjNiLWExZmUtNTdiY2NkZWIwYTMzJDc2ZjFjZDliLWM0MWMtNDQzNC05NTM5LTY3ZWU3OTBmNTY0YyRjMzZjY2NjNC1hMGVhLTQwZWUtYTZjYy0zNzBkNGQ2ZTVlN2YkZmI1MTBhODgtZmQ5Yi00MDI4LTg3NTUtNWU4ZWRhNTczMjc1JGY4MGM1NGFiLTFkMGMtNDYyNy1iZWUzLWM3MjI3MDNhNTg5ZCRiYmY1Y2M0ZC04Yjk0LTQzMWItODlkMi1lMGE5MWE3MjhmMWEkYmRiM2EyM2QtMjFiMC00OTMyLTkwOWItYzdiMjU0YWUzOGVhJDE5Mzg2OTU5LTU1ZWYtNDFkYy1hYzUzLTRhYTJiYWE0OGM4YyRlNmRlYTkxZC1lMTE0LTRkYmMtYWM0Mi0xN2FiNjVkMGE2NGYkN2Q3NWNjYTctNjZlYi00MTM2LWI5YTUtNGYwN2I3MGI5MmE4JDk5MzM1ZmQ1LTAxZDEtNGJjMC1hMmNlLWFiOTEyMTJhNjA4MSRjNTM3ZDJkOC0yMGUzLTQ4YmEtODBkMi1hNzM0ZmFjNjk3ZjgkZDBkYzQzODctOTk4MS00Y2IyLTliZTEtYWQzYzg1MzQwYmYxFCsDO2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZGQCGw9kFgQCAw8PZBYCHgdvbmNsaWNrBRNqYXZhc2NyaXB0OnBvcFdpbigpZAIFDzwrAA0AZAIZDxYCHwcFyAU8ZGl2IGNsYXNzPSJmdHJsZWZ0Ij48YSBocmVmPSJodHRwOi8vaXNjLmN1eWFob2dhY291bnR5LnVzLyI+PC9hPjwvZGl2Pgo8IS0tZnRybGVmdC0tPgo8ZGl2IGNsYXNzPSJmdHJsZWZ0Ij5DdXlhaG9nYSBDb3VudHkgU2hlcmlmZjxiciAvPgoxMjE1IFdlc3QgM3JkIFN0cmVldDxiciAvPgpDbGV2ZWxhbmQsIE9oaW8gNDQxMTMgPGJyIC8+CigyMTYpIDQ0My02MDAwPGJyIC8+CjxhIGhyZWY9Im1haWx0bzpzaGN1eUBjdXlhaG9nYWNvdW50eS51cyI+c2hjdXlAY3V5YWhvZ2Fjb3VudHkudXM8L2E+PC9kaXY+CjxkaXYgY2xhc3M9ImZ0cmxlZnQiPjxhIGhyZWY9Imh0dHA6Ly93d3cueW91dHViZS5jb20vdmlld19wbGF5X2xpc3Q/cD01QjQ1Qjg4NDkwRDY2RTI3Ij48aW1nIGFsdD0iIiBzcmM9Ii9pbWdfc2hlcmlmZi9Zb3V0dWJlLUljb24uZ2lmIiAvPjwvYT4gPGEgaHJlZj0iaHR0cDovL3d3dy5mYWNlYm9vay5jb20vcGFnZXMvQ2xldmVsYW5kLU9IL0N1eWFob2dhLUNvdW50eS1TaGVyaWZmLzI4OTQ5NjE2OTMzNyI+PGltZyBhbHQ9IiIgc3JjPSIvaW1nX3NoZXJpZmYvZmFjZWJvb2staWNvbi5naWYiIC8+PC9hPiA8YSBocmVmPSJodHRwOi8vdHdpdHRlci5jb20vY3V5YWhvZ2FzaGVyaWZmIj48aW1nIGFsdD0iIiBzcmM9Ii9pbWdfc2hlcmlmZi90d2l0dGVyLWljb24uZ2lmIiAvPjwvYT48L2Rpdj4KPGRpdiBjbGFzcz0iZnRybGVmdCI+PC9kaXY+ZBgCBR5fX0NvbnRyb2xzUmVxdWlyZVBvc3RCYWNrS2V5X18WAgUVY3RsMDAkbWFzdGVyTmF2JE1lbnUxBQ9jdGwwMCRUcmVlVmlldzEFKGN0bDAwJENvbnRlbnRQbGFjZUhvbGRlcjEkZ3ZTZWFyY2hSZXN1bHQPZ2SfmglnkwdD8WVA7pDGwbN4hJ+ocw=='
    }
    form_data = urllib.urlencode(form_values)

    request = urllib2.Request(form_url, form_data)
    request.get_full_url()
    request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:22.0) Gecko/20100101 Firefox/22.0')
    request.add_header('X-MicrosoftAjax', 'Delta=true') # Necessary for postback
    request.add_header('Referer', 'http://sheriff.cuyahogacounty.us/en-US/Foreclosure-Property-Search.aspx')
    response = opener.open(request).read()

    return response


def write_to_file(data, filename):
    """Write data to a file in our data directory."""
    outfile_path = _OUTPUT_DIR + '/' + filename
    outfile = file(outfile_path, 'w')
    outfile.write(data)
    outfile.close()
    return outfile_path


def read_from_file(filename):
    """Read and return all data from a file in our data directory."""
    path = _OUTPUT_DIR + '/' + filename
    infile = file(path, 'r')
    data = infile.read()
    infile.close()
    return data


def save_response(response, parcel_num):
    """Save response to file."""
    filename = parcel_num + '-orig.txt'
    return write_to_file(response, filename)


def get_search_response_from_file(parcel_num):
    """Read a pre-saved (original) response from existing file."""
    filename = parcel_num + '-orig.txt'
    return read_from_file(filename)


def parse_num_properties(response):
    """Get the number of properties returned from within the response."""
    m = re.search('<span id="ctl00_ContentPlaceHolder1_lblNumberOfRecordsFound">(\d*)</span>', response)
    if len(m.groups()) > 0:
        return int(m.group(1))
    else:
        _logger.debug('Error: Number of properties unknown.')
        return 0


def clean_response(response):
    """Clean up and return the search response.

    It comes with initial data before and after the HTML. Remove that.
    Then prettify with BeautifulSoup.

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


def get_parcel_info(parcel_num, live_mode=_LIVE_MODE):
    """Submit the form, output to file, and parse."""
    if live_mode:
        response = run_parcel_search(parcel_num)
        outfile_path = save_response(response, parcel_num)
        print "Original response saved to '" + outfile_path + "'."
    else:
        response = get_search_response_from_file(parcel_num)

    num_properties = parse_num_properties(response)
    print str(num_properties) + " Property records returned."

    response = clean_response(response)
    cleaned_response_path = write_to_file(response, parcel_num + '.html')
    print "Cleaned-up response saved to '" + cleaned_response_path + "'."

    return parse_properties(response, num_properties)


def usage():
    print "Usage: " + sys.argv[0] + " [-h|--help] [-p|--parcel] <parcel_id> [-c|cached]"


def main(argv):
    # Global cmd-line parameter -based variables
    global _live_mode
    _live_mode = True
    global _deploy
    _parcel_num = ''

    try:
        opts, args = getopt.getopt(argv, "hp:c", ["help", "parcel", "cached"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(2)
        elif opt in ("-p", "--parcel"):
            _parcel_num = arg
        elif opt in ("-c", "--cached"):
            _live_mode = False

    if _parcel_num == '':
        usage()
        sys.exit(2)

    get_parcel_info(_parcel_num, _live_mode)

if __name__ == "__main__":
    main(sys.argv[1:])