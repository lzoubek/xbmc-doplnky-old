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

import re,os,urllib
import xbmcaddon,xbmc,xbmcgui,xbmcplugin
import util,resolver
import youtuberesolver as youtube
__scriptid__   = 'plugin.video.re-play.cz'
__scriptname__ = 're-play.cz'
__addon__      = xbmcaddon.Addon(id=__scriptid__)
__language__   = __addon__.getLocalizedString

BASE_URL='http://re-play.cz/category/videoarchiv/'

def list_page(number=-1):
	url = BASE_URL
	if number > 0:
		url+='page/'+str(number)
	page = util.request(url)
	data = util.substr(page,'<div id=\"archive','end #archive')
	pattern = '<div class=\"cover\"><a href=\"(?P<url>[^\"]+)(.+?)title=\"(?P<name>[^\"]+)(.+?)<img src=\"(?P<logo>[^\"]+)(.+?)<p class=\"postmetadata\">(?P<fired>[^<]+)(.+?)<p>(?P<plot>[^<]+)'
	for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL):
		name = '%s - %s' % (m.group('name'),m.group('fired').replace('/','')) 
		util.add_video(name,{'play':m.group('url')},m.group('logo'),{'Plot':m.group('plot')})
	data = util.substr(page,'<div class=\"navigation\">','</div>')
	for m in re.finditer('<a href=\"(.+?)/page/(?P<page>[\d]+)',data,re.IGNORECASE | re.DOTALL):
		name = 'Na stranu %s' % m.group('page')
		util.add_dir(name,{'page':m.group('page')})
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def play(url):
	data = util.substr(util.request(url),'<div class=\"zoomVideo','</div>')
	m = re.search('<object(.+?)data=\"(?P<url>http\://www\.youtube\.com/v/[^\&]+)',data,re.IGNORECASE | re.DOTALL)
	if not m == None:
		youtube.__eurl__ = url
		streams = resolver.resolve(m.group('url'))
		if not streams == None and len(streams)>0:
			util.reportUsage(__scriptid__,__scriptid__+'/play')
			stream = streams[0]
			print 'Sending %s to player' % stream
			li = xbmcgui.ListItem(path=stream,iconImage='DefaulVideo.png')
			return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
		

p = util.params()
if p=={}:
	xbmc.executebuiltin('RunPlugin(plugin://script.usage.tracker/?do=reg&id=%s)' % __scriptid__)
	list_page()
if 'page' in p.keys():
	list_page(p['page'])
if 'play' in p.keys():
	play(p['play'])
