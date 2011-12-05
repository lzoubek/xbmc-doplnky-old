# -*- coding: UTF-8 -*-
#/*
# *      Copyright (C) 2011 Libor Zoubek
# *
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# */
import os,re,sys,urllib,urllib2,traceback,cookielib,random,time
UA='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'

TRACKER_URL='http://www.google-analytics.com/__utm.gif'

##
# initializes urllib cookie handler
def init_urllib():
	cj = cookielib.LWPCookieJar()
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	urllib2.install_opener(opener)

def _request(url,info):
	# setup useragent!!
	print '[google] Submiting usage'
	req = urllib2.Request(url)
	req.add_header('User-Agent',info['useragent'])
	response = urllib2.urlopen(req)
	data = response.read()
	if 200 == response.code:
		print '[google] Usage has been submitted'
	response.close()

def _get_cookie(info):
	return '__utma='+'.'.join(info['instanceid'])+'.8;+__utmz='+info['instanceid'][0]+'.'+info['instanceid'][-1]+'.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)|utmctr=(none)'

def createInstanceID():
	return [str(random.randint(0,99999999)),str(random.randint(0,9999999999)),str(random.randint(0,9999999999)),str(random.randint(0,9999999999)),str(random.randint(0,9999999999))]


def track_usage(url,action,trackingCode,dry,info):
	params = {
	'utmac':trackingCode,
	'utms':'1', # number of 'clicks'
	'utmcs':'UTF-8', # system encoding
	'utmdt':action, # page title
	'utmhn':url, # url-encoded target url
	'utmhid':random.randint(0,9999999999), #random number
	'utmje':'0', # do we have java? 1 = yes, 0 = no
	'utmn':time.time(), # unique for each request to avoid caching
	'utmp':'/'+action, # page that has been visited
	'utmsc':info['colordepth'], # color depth
	'utmsr':info['resolution'], # screen resolution
	'utmul':info['language'], # system language
	'utmr':'-', # referal - 0 = none
	'utmwv':'5.2.2', # version of tracking client
	'utmcc':_get_cookie(info),
	'utmu':'q~' # what is this about?
	}
	req = TRACKER_URL+'?'+urllib.urlencode(params)
	if not dry:
		_request(req,info)

