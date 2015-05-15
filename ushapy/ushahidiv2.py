
#!/usr/bin/env python
""" Read/write to Ushahidi v2.7 instances

Ushapy requirements: 
* Get all Ushahidi reports (id, title, description text, categories, formfield values, date), filtered by start/end dates, categories, form, formfields
* Get all Ushahidi messages (id, message text, source, reporterid, reportid), filtered by start/end dates, reporters
* Change category values on an Ushahidi report
* Change formfield values on an Ushahidi report
* Add categories and subcategories (allow user to hide these categories) to Platform
* Add report to platform

Sara-Jayne Terp
2014
"""

import requests
from requests.auth import HTTPBasicAuth
import time
import json
import datetime
#import read_write_csv


""" Add new set of categories (with subcategories) to Ushahidi Platform

Parameters:
* mapurl: String containing URL of Ushahidi Platform instance, e.g. http://www.mymap.com/
* Categories: List of categories, as [categoryname, description, parentcategoryname, color]
  if description is empty, it's set to the category location_name
  if color is empty, it's set to black #000
* Addedcats: List of categories added to map, as [categoryname]

Note that Ushahidi only allows 2 levels of category, e.g. a category cannot be both a
parent category and a child category.
"""
def add_categories_to_map(mapurl, categories):
	addedcats = []
	return(addedcats)


""" Change the categories list on an Ushahidi report

Parameters:
* mapurl: String containing URL of Ushahidi Platform instance, e.g. http://www.mymap.com/
* reportid: Ushahidi id for one of the Ushahidi Platform reports. 
* adds: list of categories to add to the report
* removes: list of categories to remove from the report
* removeall: flag set to remove all categories from report, before adding the "adds" categories

"""
def change_report_categories(mapurl, reportid, adds=[], removes=[], removeall=False):
	return()



""" Get one report from ushahidi website, given its id and map url

Parameters:
* mapurl: String containing URL of Ushahidi Platform instance, e.g. http://www.mymap.com/
* reportid: Ushahidi id for one of the Ushahidi Platform reports. 
* payload

"""
def get_ush_report(mapurl, reportid):
	#Put list of sites into a dictionary
	response = requests.get(url=mapurl+"api?task=incidents&by=incidentid&id="+str(reportid))
	reportsjson = json.loads(response.text)
	payload = reportsjson['payload']['incidents'][0]
	return(payload)


""" Get reports from ushahidi website

Parameters:
* mapurl: String containing URL of Ushahidi Platform instance, e.g. http://www.mymap.com/
* reports

"""
def get_all_reports(mapurl):
	#Put list of sites into a dictionary
	reports = []
	numreports = get_number_of_ush_reports(mapurl)
	numcalls = numreports/100
	if numcalls < 100 or numcalls%100 != 0:
		numcalls += 1
	for call in range(0, numcalls):
		startid = str(call*100)
		if call == 0:
			response = requests.get(url=mapurl+"api?task=incidents&limit=100")  #Ush api crashes if sinceid=0
		else:
			response = requests.get(url=mapurl+"api?task=incidents&by=sinceid&id="+startid+"&limit=100")
		reportsjson = json.loads(response.text)
		for sitedetails in reportsjson['payload']['incidents']:
			reports += [sitedetails];
	return reports



""" Get number of reports on an Ushahidi Platform site

Parameters:
* mapurl: String containing URL of Ushahidi Platform instance, e.g. http://www.mymap.com/
* numreports: number of reports on the Ushahidi platform, at the time the call was made

"""
def get_number_of_ush_reports(mapurl):
	response = requests.get(url=mapurl+"api?task=incidentcount")
	numjson = json.loads(response.text)
	numreports = int(numjson['payload']['count'][0]['count'])	
	return numreports



""" Use ushahidi site's categories list to convert text categories list into ids

Parameters:
* mapurl: String containing URL of Ushahidi Platform instance, e.g. http://www.mymap.com/
* catslist
* mapcategories
* catidslist

"""
def cats_to_catids(mapurl, catslist, mapcategories={}):
	catids = [];
	if mapcategories == {}:
		response = requests.get(url=mapurl+"api?task=categories");
		catsjson = json.loads(response.text);
		for cat in catsjson['payload']['categories']:
			mapcategories.setdefault(cat['category']['title'], cat['category']['id']);
	catnames = catslist.split(",");
	for catname in catnames:
		if catname in mapcategories:
			catids += [mapcategories[catname]];
	catidslist = ",".join(catids);
	return(catidslist)



""" Convert report output by Ushahidi report view API into a structure that can be 
input into the Ushahidi report edit api.  Yes, yes, I know they should be the 
same format, but life.

Parameters:
* viewpayload
* editload

"""
def reformat_ush_api_report_view_to_edit(viewpayload):
	editload = {}
	viewdetails = viewpayload['incident']
	viewcategories = viewpayload['categories']
	editload['incident_id'] = viewdetails['incidentid']
	editload['incident_title'] = viewdetails['incidenttitle']
	editload['incident_description'] = viewdetails['incidentdescription']
	editload['latitude'] = viewdetails['locationlatitude']
	editload['longitude'] = viewdetails['locationlongitude']
	editload['location_name'] = viewdetails['locationname']
	editload['location_id'] = viewdetails['locationid']
	editload['incident_active'] = viewdetails['incidentactive']
	editload['incident_verified'] = viewdetails['incidentverified']
	t = datetime.datetime.strptime(viewdetails['incidentdate'],  "%Y-%m-%d %H:%M:%S")
	editload['incident_date'] = t.strftime("%m/%d/%Y")
	editload['incident_hour'] = t.strftime("%I")
	editload['incident_minute'] = t.strftime("%M")
	editload['incident_ampm'] = t.strftime("%p").lower()
	cats = []
	for cat in viewcategories: 
		cats += [str(cat['category']['id'])]
	editload['incident_category'] = ','.join(cats)
	return(editload)



""" Edit ushahidi report  

Parameters:
* mapurl: String containing URL of Ushahidi Platform instance, e.g. http://www.mymap.com/
* r

"""
def edit_report(mapurl, payload, username, password):
	editload = payload
	editload['task'] = 'reports'
	editload['action'] = 'edit'
	r = requests.post(mapurl+"api?task=reports", data=editload, auth=(username, password));
	return(r)



""" Push entry with photo attached to an Ushahidi V2.7 repo 

Parameters:
* mapurl: String containing URL of Ushahidi Platform instance, e.g. http://www.mymap.com/
* title
* description
* lat
* lon
* location
* categories
* photopath
* photoname
* newreport

#date, hour, minute, ampm are all mandatory fields 
#Url, Technology, Country are all custom formfields in my site; use similar
"""
def add_report_to_platform(mapurl, title, description, lat, lon, location, categories, 
	photopath="", photoname="", newreport=True):
#format if you have custom formfields yourself
	now = time.gmtime();
	payload = { \
	'task': 'report', \
	'incident_title': title, \
	'incident_description': description, \
	'incident_category': cats_to_catids(mapurl, categories), \
	'latitude': lat, \
	'longitude': lon, \
	#'Url': mapurl, \
	#'Technology': sitedesc['technology'], \
	#'Country': sitedesc['country'], \
	'incident_date': time.strftime('%m/%d/%Y', now), \
	'incident_hour': time.strftime('%I', now), \
	'incident_minute': time.strftime('%M', now), \
	'incident_ampm': time.strftime('%p', now).lower(), \
	'location_name': location, \
	};

	#Treat reports with images attached slightly differently
	if photoname == "":
		r = requests.post(mapurl+"api", data=payload);
	else:
		payload['incident_photo[]'] = "@"+photoname+";filename="+photoname+";type=image/jpeg";
		imagefiles = {photoname: open(photoname, 'rb')};
		r = requests.post(mapurl+"api", data=payload, files=imagefiles);

	return(r)


def add_message_to_platform(mapurl, message_text, message_date_in, message_type, 
	service_messageid, message_level, reporter_id, message_from, message_to, message_detail, 
	parent_id, incident_id, latitude, longitude, 
	username, password, newmessage=True):
	
	#Make sure there's a timestamp on this message
	if message_date_in == '':
		now = time.gmtime();
		message_date = time.strftime("%Y-%m-%d %H:%M:%S", now);
	else:
		message_date = message_date_in;

	payload = { \
	'task': 'messages', \
	'action': 'add', \
	'message_text': message_text, \
	'message_date': message_date, \
	'message_type': message_type, \
	'service_messageid': service_messageid, \
	'message_level': message_level, \
	'reporter_id': reporter_id, \
	'message_from': message_from, \
	'message_to': message_to, \
	'message_detail': message_detail, \
	'parent_id': parent_id, \
	'incident_id': incident_id, \
	'latitude': latitude, \
	'longitude': longitude \
	};

	r = requests.post(mapurl+"api", data=payload, auth=(username, password));

	return(r)


def add_reporter_to_platform(mapurl, service_id, service_account, level_id, reporter_first, reporter_last,
	reporter_email, reporter_phone, reporter_ip, reporter_date, location_name, latitude, longitude, 
	username, password, newservice=True):
	
	payload = { \
	'task': 'reporters', \
	'action': 'add', \
	'service_id': service_id, \
	'service_account': service_account, \
	'level_id': level_id, \
	'reporter_first': reporter_first, \
	'reporter_last': reporter_last, \
	'reporter_email': reporter_email, \
	'reporter_phone': reporter_phone, \
	'reporter_ip': reporter_ip, \
	'reporter_date': reporter_date, \
	'location_id': '', \
	'location_name': location_name, \
	'latitude': latitude, \
	'longitude': longitude \
	};
	
	r = requests.post(mapurl+"api", data=payload, auth=(username, password));
	
	return(r)


def add_service_to_platform(mapurl, service_name, service_description, service_url, service_api,
	username, password, newservice=True):
	
	payload = { \
	'task': 'services', \
	'action': 'add', \
	'service_name': service_name, \
	'service_description': service_description, \
	'service_url': service_url, \
	'service_api': service_api \
	};

	r = requests.post(mapurl+"api", data=payload, auth=(username, password));

	return(r)


def edit_service(mapurl, service_id, service_name, service_description, service_url, service_api,
	username, password, newservice=True):
	
	payload = { \
	'task': 'services', \
	'action': 'edit', \
	'service_id': service_id, \
	'service_name': service_name, \
	'service_description': service_description, \
	'service_url': service_url, \
	'service_api': service_api \
	};
	
	r = requests.post(mapurl+"api", data=payload, auth=(username, password));
	
	return(r)

