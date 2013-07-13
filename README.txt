This is a web "scraper" for property (real estate) foreclosures in Ohio's Cuyahoga County, gathering data from the County Sheriff's website.

The County Sheriff's website was redesigned a year-or-two ago and most parts of the scraper no longer work. The new site uses .NET asynchronous postbacks, which have proved slightly more complicated to interact with and parse.

Current work is on get_property.py -- which searches for an individual property. The plan is to finish this individual property search functionality, then rebuild the original functionality that gathered information on all properties (exporting as XML.)