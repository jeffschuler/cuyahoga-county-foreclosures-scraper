#!/usr/bin/python

import scrapelib
import statics

s = scrapelib.Scraper(requests_per_minute=10, accept_cookies=True,
                      follow_robots=True)

property_search_page = 'http://sheriff.cuyahogacounty.us/en-US/Foreclosure-Property-Search.aspx'
s.urlopen(property_search_page)

property_search_form = 'http://sheriff.cuyahogacounty.us/en-US/PropertySearch.aspx?LanguageCD=en-US&amp;ItemKey=26945&amp;pb=y'

statics.CITY_FORM_CITY_CODES['Berea']
statics.CITY_FORM_ID

import urllib, urllib2
raw_params = {statics.CITY_FORM_ID: statics.CITY_FORM_CITY_CODES['Berea']}
params = urllib.urlencode(raw_params)
request = urllib2.Request(property_search_form, params)
page = urllib2.urlopen(request)
info = page.info()