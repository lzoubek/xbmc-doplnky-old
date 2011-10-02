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

import urllib2,re,os,random
import xbmcaddon,xbmc,xbmcgui,xbmcplugin
import util,resolver

__scriptid__   = 'plugin.video.zkouknito.cz'
__scriptname__ = 'zkouknito.cz'
__addon__      = xbmcaddon.Addon(id=__scriptid__)
__language__   = __addon__.getLocalizedString

BASE_URL='http://zkouknito.cz/'

def list_categories():
	data = util.substr(util.request(BASE_URL+'videa'),'<ul class=\"category','</ul')
	util.add_dir('Online TV',{'cat':'http://www.zkouknito.cz/online-tv'})
	pattern='<a href=\"(?P<link>[^\"]+)[^>]+>(?P<cat>[^<]+)</a>'	
	for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL):
		if m.group('cat').find('18+') > 0:
			continue
		util.add_dir(m.group('cat'),{'cat':BASE_URL+m.group('link')})
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def add_video(name,params,logo,infoLabels):
	if not logo == '':
		if logo.find('/') == 0:
			logo = logo[1:]
		if logo.find('http://') < 0:
			logo = BASE_URL+logo
	return util.add_video(name,params,logo,infoLabels)

def list_category(url):
	page = util.request(url)
	q = url.find('?')
	if q > 0:
		url = url[:q]
	data = util.substr(page,'<div id=\"videolist','<div class=\"paging-adfox\">')
	pattern='<div class=\"img-wrapper\"><a href=\"(?P<url>[^\"]+)\" title=\"(?P<name>[^\"]+)(.+?)<img(.+?)src=\"(?P<img>[^\"]+)(.+?)<p class=\"dsc\">(?P<plot>[^<]+)'
	for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL):
		add_video(m.group('name'),{'play':BASE_URL+m.group('url')},m.group('img'),{'Plot':m.group('plot')})
	data = util.substr(page,'<div class=\"jumpto\"','</div>')
	print data
	pages = re.search('<strong>([\d]+)',data,re.IGNORECASE | re.DOTALL).group(1)
	current = re.search('value=\"([\d]+)',data,re.IGNORECASE | re.DOTALL).group(1)
	
	data = util.substr(page,'<p class=\"paging','</p>')
	for m in re.finditer('<a href=\"(?P<url>[^\"]+)\"><img(.+?)alt=\"(?P<name>[^\"]+)\" />',data,re.IGNORECASE | re.DOTALL):
		name = '[B] %s / %s - %s [/B]' % (current,pages,m.group('name'))
		util.add_dir(name,{'cat':url+m.group('url')})
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def play(url):
	data = util.request(url)
	data = util.substr(data,'<div class=\"player\"','</div>')
	m = re.search('<param name=\"movie\" value=\"(?P<url>[^\"]+)',data,re.IGNORECASE | re.DOTALL)
	if not m == None:
		streams = resolver.resolve(m.group('url'))
		if streams == None:
			return 	xbmcgui.Dialog().ok(__scriptname__,__language__(30000))
		if len(streams) > 0:
			print 'Sending %s to player' % streams[0]
			li = xbmcgui.ListItem(path=streams[0],iconImage='DefaulVideo.png')
			return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
	n = re.search('<param name=\"url\" value=\"(?P<url>[^\"]+)',data,re.IGNORECASE | re.DOTALL)
	if not n == None:
		print 'Sending %s to player' % n.group('url')
		li = xbmcgui.ListItem(path=n.group('url'),iconImage='DefaulVideo.png')
		return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
	
params=util.params()
if params=={}:
	list_categories()
if 'cat' in params.keys():
	list_category(params['cat'])
if 'play' in params.keys():
	play(params['play'])
