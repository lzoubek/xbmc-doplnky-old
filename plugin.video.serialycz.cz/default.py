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
import urllib2,re,os,md5
import xbmcaddon,xbmc,xbmcgui,xbmcplugin
import util

__scriptid__   = 'plugin.video.serialycz.cz'
__scriptname__ = 'serialycz.cz'
__addon__      = xbmcaddon.Addon(id=__scriptid__)
__language__   = __addon__.getLocalizedString

BASE_URL='http://www.serialycz.cz/'

def _image(name,link):
	# load image from disk or download it (slow for each serie, thatwhy we cache it)
	local = xbmc.translatePath(__addon__.getAddonInfo('profile'))
	if not os.path.exists(local):
		os.makedirs(local)
	m = md5.new()
	m.update(name)
	local = os.path.join(local,m.hexdigest()+'.png')
	if os.path.exists(local):
		return local
	else:
		data = util.substr(util.request(link),'<div id=\"archive-posts\"','</div>')
		m = re.search('<img(.+?)src=\"(?P<img>[^\"]+)', data, re.IGNORECASE | re.DOTALL)
		if not m == None:
			print ' Downloading %s' % m.group('img')
			data = util.request(m.group('img'))
			f = open(local,'w')
			f.write(data)
			f.close()
			return local

def list_series():
	data = util.substr(util.request(BASE_URL),'<div id=\"primary\"','</div>')
	pattern='<a href=\"(?P<link>[^\"]+)[^>]+>(?P<name>[^<]+)</a>'	
	util.add_dir('[B]Nejnovější epizody[/B]','newest=list','')
	for m in re.finditer(pattern, util.substr(data,'Seriály</a>','</ul>'), re.IGNORECASE | re.DOTALL):
		util.add_dir(m.group('name'),'serie='+m.group('link')[len(BASE_URL):],_image(m.group('name'),m.group('link')))
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def list_episodes(url):	
	data = util.request(BASE_URL+url)
	data = util.substr(data,'<div id=\"archive-posts\"','</div>')
	m = re.search('<a(.+?)href=\"(?P<url>[^\"]+)', data, re.IGNORECASE | re.DOTALL)
	if not m == None:
		data = util.request(m.group('url'))
		for m in re.finditer('<a href=\"(?P<link>[^\"]+)(.+?)(<strong>|<b>)(?P<name>[^<]+)', util.substr(data,'<div class=\"entry-content','</div>'), re.IGNORECASE | re.DOTALL):
			util.add_video(m.group('name'),m.group('link')[len(BASE_URL):])
		xbmcplugin.endOfDirectory(int(sys.argv[1]))

def newest_episodes():
	data = util.substr(util.request(BASE_URL+'category/new-episode/'),'<div id=\"archive-posts\"','</ul>')
	pattern='<img(.+?)src=\"(?P<img>[^\"]+)(.+?)<a href=\"(?P<link>[^\"]+)[^>]+>(?P<name>[^<]+)</a>'	
	for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL):
		util.add_video(m.group('name'),m.group('link')[len(BASE_URL):],0,m.group('img'))	
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def play(url):
	data = util.substr(util.request(BASE_URL+url),'<div id=\"content\"','<div id=\"sidebar')
	stream_url = util.resolve_stream(data)
	if stream_url == '':
		xbmcgui.Dialog().ok(__scriptname__,'Video neni mozne prehrat,[CR]zdroj tento zdroj neni a nebude podporovan')
		return
	if not stream_url == None:
		print 'Sending %s to player' % stream_url
		li = xbmcgui.ListItem(path=stream_url,iconImage='DefaulVideo.png')
		return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
	xbmcgui.Dialog().ok(__scriptname__,'Prehravani vybraneho videa bud zatim neni[CR]podporovano nebo video neni k dispozici.')

p = util.params()
if p=={}:
	list_series()
if 'newest' in p.keys():
	newest_episodes()
if 'serie' in p.keys():
	list_episodes(p['serie'])
if 'play' in p.keys():
	play(p['play'])
